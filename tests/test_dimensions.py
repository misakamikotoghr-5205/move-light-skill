import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('dimension_plan', ROOT/'skill/move-light/scripts/plan.py')
planner = importlib.util.module_from_spec(spec); spec.loader.exec_module(planner)


def request(items):
    return {'move_date': '2026-11-05', 'budget_fen': 50000, 'box_capacity_l': 40, 'box_max_weight_kg': 15,
            'box_dimensions_cm': [40, 30, 30], 'items': items,
            'quotes': [{'id': 'complete', 'name': 'Complete estimate', 'base_fen': 20000, 'per_box_fen': 500, 'extra_fees_fen': 0, 'fees_complete': True, 'capacity_l': 1000}]}


def item(identifier='small', dimensions=None, volume=2):
    value = {'id': identifier, 'name': identifier, 'quantity': 1, 'volume_l': volume, 'weight_kg': 1, 'fragile': True, 'essential': True}
    if dimensions is not None: value['dimensions_cm'] = dimensions
    return value


class DimensionTests(unittest.TestCase):
    def test_long_thin_item_is_not_packed_just_because_its_litres_fit(self):
        data = request([item('long-poster-tube', [70, 5, 5], 2), item('mug', [15, 12, 10], 2)])
        result = planner.plan(data, '2026-11-04')
        self.assertEqual(result['box_count'], 1)
        self.assertEqual([unit['unit_id'] for unit in result['loose_items']], ['long-poster-tube:1'])
        self.assertIn('dimensions_exceed_box', result['loose_items'][0]['reason_codes'])
        self.assertEqual(result['geometry']['rejected_unit_ids'], ['long-poster-tube:1'])
        self.assertIsNone(result['recommendation'], 'unpriced loose-item handling still blocks a quote recommendation')

    def test_orthogonal_rotation_can_fit_without_requiring_the_authored_axis_order(self):
        data = request([item('rotated', [28, 39, 20], 22)])
        result = planner.plan(data, '2026-11-04')
        self.assertEqual(result['loose_items'], [])
        self.assertEqual(result['geometry']['checked_units'], 1)
        self.assertTrue(result['boxes'][0]['items'][0]['axis_fit_checked'])
        self.assertFalse(result['geometry']['layout_verified'])

    def test_measured_capacity_and_bounding_volume_override_optimistic_estimates(self):
        data = request([item('cube-a', [20, 20, 20], 1), item('cube-b', [20, 20, 20], 1)])
        data['box_dimensions_cm'] = [30, 20, 20]  # 12 L, not the nominal 40 L.
        result = planner.plan(data, '2026-11-04')
        self.assertEqual(result['effective_box_capacity_l'], 12)
        self.assertEqual(result['box_count'], 2)
        self.assertEqual(result['total_item_volume_l'], 2)
        self.assertTrue(all(box['volume_l'] == 8 for box in result['boxes']))
        self.assertTrue(all(box['items'][0]['packing_volume_l'] == 8 for box in result['boxes']))

    def test_missing_dimensions_remain_unknown_and_inputs_are_not_modified(self):
        data = request([item('unmeasured')]); before = copy.deepcopy(data)
        result = planner.plan(data, '2026-11-04')
        self.assertEqual(result['geometry']['checked_units'], 0)
        self.assertEqual(result['geometry']['unchecked_unit_ids'], ['unmeasured:1'])
        self.assertFalse(result['boxes'][0]['items'][0]['axis_fit_checked'])
        self.assertEqual(data, before)
        self.assertIn('边长未核对', planner.render(result))
        del data['box_dimensions_cm']
        data['items'][0]['dimensions_cm'] = [15, 10, 10]
        self.assertEqual(planner.plan(data, '2026-11-04')['geometry']['checked_units'], 0)

    def test_invalid_dimensions_fail_before_a_plan_is_written(self):
        for dimensions in ([1, 2], [1, 2, 0], [1, 2, -3], [True, 2, 3], [float('nan'), 2, 3], '40x30x20'):
            data = request([item('bad', dimensions)])
            with self.subTest(dimensions=dimensions), self.assertRaises(ValueError):
                planner.plan(data, '2026-11-04')
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary); path = folder/'input.json'; output = folder/'output'
            data = request([item('bad', [1, 2, 0])]); path.write_text(json.dumps(data), encoding='utf-8')
            result = subprocess.run([sys.executable, str(ROOT/'skill/move-light/scripts/plan.py'), str(path), '--out', str(output)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main()
