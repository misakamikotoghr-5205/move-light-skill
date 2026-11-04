import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('move_plan', ROOT/'skill/move-light/scripts/plan.py'); module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
BASE = json.loads((ROOT/'examples/family.json').read_text())
class PlannerTests(unittest.TestCase):
    def test_every_unit_once_and_capacity_holds(self):
        result = module.plan(BASE, '2026-11-04')
        units = [unit for box in result['boxes'] for unit in box['items']] + result['loose_items']
        self.assertEqual(len(units), sum(item['quantity'] for item in BASE['items']))
        self.assertEqual(len({unit['unit_id'] for unit in units}), len(units))
        for box in result['boxes']:
            self.assertLessEqual(box['volume_l'], BASE['box_capacity_l']); self.assertLessEqual(box['weight_kg'], BASE['box_max_weight_kg'])
            self.assertEqual(len({unit['group'] for unit in box['items']}), 1)
    def test_unknown_fees_never_win_over_complete_quote(self):
        result = module.plan(BASE, '2026-11-04')
        self.assertEqual(result['recommendation'], 'complete')
        self.assertFalse(next(quote for quote in result['quotes'] if quote['id']=='unknown')['rankable'])
    def test_oversized_item_and_vehicle_shortfall(self):
        data = copy.deepcopy(BASE); data['items'][0]['volume_l'] = 90
        result = module.plan(data, '2026-11-04')
        self.assertEqual(len(result['loose_items']), 4); self.assertIsNone(result['recommendation'])
        data = copy.deepcopy(BASE); data['quotes'][0]['capacity_l'] = 10
        self.assertFalse(module.plan(data, '2026-11-04')['quotes'][0]['rankable'])
    def test_missing_vehicle_capacity_not_assumed(self):
        data = copy.deepcopy(BASE); del data['quotes'][0]['capacity_l']
        self.assertIsNone(module.plan(data, '2026-11-04')['recommendation'])
    def test_dates_are_not_silently_rescheduled(self):
        result = module.plan(BASE, '2026-11-19')
        self.assertEqual(result['tasks'][0]['date'], '2026-11-06'); self.assertEqual(result['tasks'][0]['status'], 'overdue')
    def test_no_mutation_and_deterministic(self):
        before = copy.deepcopy(BASE)
        self.assertEqual(module.plan(BASE,'2026-11-04'), module.plan(BASE,'2026-11-04')); self.assertEqual(BASE,before)
    def test_invalid_values(self):
        for field, value in [('box_capacity_l',float('nan')),('budget_fen',12.5),('box_max_weight_kg',True)]:
            data = copy.deepcopy(BASE); data[field]=value
            with self.assertRaises(ValueError): module.plan(data,'2026-11-04')
        data=copy.deepcopy(BASE); data['items'].append(data['items'][0])
        with self.assertRaises(ValueError): module.plan(data,'2026-11-04')
    def test_exact_cent_quote_math(self):
        result = module.plan(BASE,'2026-11-04'); quote=result['quotes'][0]
        self.assertEqual(quote['total_fen'],35000+1200*result['box_count'])
        self.assertIn('¥',module.render(result))
    def test_non_object_quotes_fail_cleanly_before_any_plan_is_written(self):
        for quote in (None, 'unconfirmed', 500, []):
            data = copy.deepcopy(BASE); data['quotes'] = [quote]
            with self.subTest(quote=quote), self.assertRaisesRegex(ValueError, 'quote must be an object'):
                module.plan(data, '2026-11-04')
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); source = root/'input.json'; output = root/'output'
            data = copy.deepcopy(BASE); data['quotes'] = [None]
            source.write_text(json.dumps(data), encoding='utf-8')
            result = subprocess.run([sys.executable, str(ROOT/'skill/move-light/scripts/plan.py'), str(source), '--today', '2026-11-04', '--out', str(output)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn('quote must be an object', result.stderr)
            self.assertNotIn('Traceback', result.stderr)
            self.assertFalse(output.exists())
if __name__=='__main__': unittest.main()
