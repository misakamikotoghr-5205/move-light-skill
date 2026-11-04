#!/usr/bin/env python3
"""Deterministic packing heuristic, exact-cent quote comparison, dated checklist."""
import argparse
from datetime import date, timedelta
import json
import math
from pathlib import Path
import sys

def number(value, name, *, positive=False, integer=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(name + ' must be a finite number')
    if value < 0 or (positive and value <= 0) or (integer and not isinstance(value, int)):
        raise ValueError(name + ' is outside its allowed range')
    return value

def validate(data):
    if not isinstance(data, dict): raise ValueError('input must be an object')
    date.fromisoformat(data['move_date'])
    number(data['budget_fen'], 'budget_fen', integer=True)
    for key in ('box_capacity_l', 'box_max_weight_kg'): number(data[key], key, positive=True)
    if not isinstance(data['items'], list) or not data['items']: raise ValueError('items must be a nonempty list')
    ids, units = set(), 0
    for item in data['items']:
        if not isinstance(item, dict): raise ValueError('item must be an object')
        for key in ('id', 'name'):
            if not isinstance(item.get(key), str) or not item[key].strip() or len(item[key]) > 200: raise ValueError('invalid item ' + key)
        if item['id'] in ids: raise ValueError('duplicate item id')
        ids.add(item['id'])
        number(item['quantity'], 'quantity', positive=True, integer=True)
        if item['quantity'] > 100: raise ValueError('quantity exceeds 100 per item')
        units += item['quantity']
        number(item['volume_l'], 'volume_l', positive=True)
        number(item['weight_kg'], 'weight_kg')
        if any(not isinstance(item.get(key), bool) for key in ('fragile', 'essential')): raise ValueError('fragile and essential must be booleans')
    if units > 1000: raise ValueError('inventory exceeds 1000 units')
    quotes = data.get('quotes', [])
    if not isinstance(quotes, list): raise ValueError('quotes must be a list')
    ids = set()
    for quote in quotes:
        if not isinstance(quote, dict): raise ValueError('quote must be an object')
        for key in ('id', 'name'):
            if not isinstance(quote.get(key), str) or not quote[key].strip(): raise ValueError('quote requires ' + key)
        if quote['id'] in ids: raise ValueError('duplicate quote id')
        ids.add(quote['id'])
        for key in ('base_fen', 'per_box_fen', 'extra_fees_fen'): number(quote[key], key, integer=True)
        if not isinstance(quote.get('fees_complete'), bool): raise ValueError('fees_complete must be boolean')
        if 'capacity_l' in quote: number(quote['capacity_l'], 'capacity_l', positive=True)
    return data

def plan(data, today):
    validate(data)
    move = date.fromisoformat(data['move_date']); now = date.fromisoformat(today)
    expanded = []
    for item in data['items']:
        group = ('essential' if item['essential'] else 'standard') + ('-fragile' if item['fragile'] else '-regular')
        for unit in range(1, item['quantity'] + 1):
            expanded.append({'unit_id': f"{item['id']}:{unit}", 'name': item['name'], 'group': group,
                             'volume_l': item['volume_l'], 'weight_kg': item['weight_kg']})
    expanded.sort(key=lambda item: (item['group'], -item['volume_l'], -item['weight_kg'], item['unit_id']))
    boxes, loose = [], []
    for unit in expanded:
        if unit['volume_l'] > data['box_capacity_l'] or unit['weight_kg'] > data['box_max_weight_kg']:
            loose.append({**unit, 'reason': 'Exceeds standard box volume or weight; quote separate handling.'}); continue
        box = next((box for box in boxes if box['group'] == unit['group'] and
                    box['volume_l'] + unit['volume_l'] <= data['box_capacity_l'] + 1e-9 and
                    box['weight_kg'] + unit['weight_kg'] <= data['box_max_weight_kg'] + 1e-9), None)
        if box is None:
            box = {'id': f"BOX-{len(boxes)+1:03}", 'group': unit['group'], 'volume_l': 0, 'weight_kg': 0, 'items': []}; boxes.append(box)
        box['items'].append(unit); box['volume_l'] += unit['volume_l']; box['weight_kg'] += unit['weight_kg']
    total_volume = sum(item['volume_l'] for item in expanded)
    # Estimate cargo space from the outside capacity of packed boxes plus loose items.
    cargo_volume = len(boxes) * data['box_capacity_l'] + sum(item['volume_l'] for item in loose)
    quotes = []
    for quote in data.get('quotes', []):
        total = quote['base_fen'] + quote['per_box_fen'] * len(boxes) + quote['extra_fees_fen']
        fits = quote.get('capacity_l', 0) >= cargo_volume if 'capacity_l' in quote else None
        eligible = quote['fees_complete'] and fits is True and not loose
        quotes.append({**quote, 'total_fen': total, 'budget_delta_fen': data['budget_fen'] - total,
                       'transport_fits': fits, 'rankable': eligible,
                       'status': 'comparable' if eligible else 'confirm_loose_item_fees' if loose else 'incomplete_fees' if not quote['fees_complete'] else 'capacity_unknown' if fits is None else 'capacity_shortfall'})
    quotes.sort(key=lambda quote: (not quote['rankable'], quote['total_fen'], quote['id']))
    tasks = []
    for days, title in [(14, '核对清单、筛选搬运报价并确认附加费'), (7, '打包低频物品，逐箱贴上箱号'), (3, '确认到达时段、电梯和搬运通道'), (1, '单独准备必需品包，拍照留存箱单'), (0, '按箱号清点装卸，核对物品和最终费用'), (-1, '先拆必需品，再按箱单逐一核对')]:
        deadline = move - timedelta(days=days)
        tasks.append({'date': deadline.isoformat(), 'title': title, 'status': 'overdue' if deadline < now else 'today' if deadline == now else 'upcoming'})
    return {'schema_version': 1, 'today': today, 'move_date': data['move_date'], 'move_date_in_past': move < now,
            'algorithm': 'first-fit decreasing, separated by essential and fragile flags; heuristic, not optimal',
            'total_units': len(expanded), 'total_item_volume_l': round(total_volume, 3), 'estimated_cargo_volume_l': round(cargo_volume, 3),
            'box_count': len(boxes), 'boxes': boxes, 'loose_items': loose, 'budget_fen': data['budget_fen'], 'quotes': quotes, 'tasks': tasks,
            'recommendation': next((quote['id'] for quote in quotes if quote['rankable']), None)}

def money(fen): return f'¥{fen // 100}.{fen % 100:02}'
def plain(value): return str(value).replace('\n', ' ').replace('\r', ' ').replace('|', '／').replace('`', 'ˋ').replace('<', '＜').replace('>', '＞')
def render(result):
    lines = ['# 搬家不掉链 · Move Light', '', f"计划日：{result['today']} · 搬家日：{result['move_date']}", '',
             f"{result['total_units']} 件物品 · {result['box_count']} 箱 · {len(result['loose_items'])} 件需单独搬运 · 预估占用 {result['estimated_cargo_volume_l']} L", '',
             '容量为箱子外部容量估计，未包含保护填充和车辆不规则空间。装箱采用确定性启发式，不保证最少箱数。', '', '## 日期清单', '']
    if result['move_date_in_past']: lines += ['搬家日期已过，请核对日期后再用此计划。', '']
    lines += [f"- [{task['status']}] {task['date']}：{task['title']}" for task in result['tasks']]
    lines += ['', '## 箱单', '']
    for box in result['boxes']:
        lines += [f"### {box['id']} · {box['group']}", f"{box['volume_l']:.1f} L / {box['weight_kg']:.1f} kg", '']
        lines += [f"- {plain(item['name'])} [{plain(item['unit_id'])}]" for item in box['items']]
        lines.append('')
    lines += ['## 单独搬运', ''] + ([f"- {plain(item['name'])} [{plain(item['unit_id'])}]：{item['reason']}" for item in result['loose_items']] or ['- 无'])
    lines += ['', '## 报价比较', '', f"预算：{money(result['budget_fen'])}", '', '| 报价 | 已知金额 | 预算差额 | 状态 |', '|---|---:|---:|---|']
    for quote in result['quotes']:
        delta = quote['budget_delta_fen']; text = ('余 ' if delta >= 0 else '超 ') + money(abs(delta))
        lines += [f"| {plain(quote['name'])} | {money(quote['total_fen'])}{' 起' if not quote['fees_complete'] else ''} | {text} | {quote['status']} |"]
    lines += ['', '只有费用已确认、车辆容量足够且无未报价散件的方案才参与排序。未知费用不能当作零元。', '', '本报告是本地计划，没有预订、付款或联系搬家公司。', '']
    return '\n'.join(lines)

def main():
    parser = argparse.ArgumentParser(description='Generate a local moving plan and box manifest.')
    parser.add_argument('input', type=Path); parser.add_argument('--today', default=date.today().isoformat()); parser.add_argument('--out', type=Path, default=Path('output'))
    args = parser.parse_args()
    try:
        result = plan(json.loads(args.input.read_text(encoding='utf-8')), args.today)
        args.out.mkdir(parents=True, exist_ok=True)
        (args.out / 'move-plan.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        (args.out / 'move-plan.md').write_text(render(result), encoding='utf-8')
        print(json.dumps({'boxes': result['box_count'], 'loose': len(result['loose_items']), 'comparable_quote': result['recommendation'], 'output': str(args.out)}, ensure_ascii=False)); return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print('Move Light: ' + str(exc), file=sys.stderr); return 2
if __name__ == '__main__': raise SystemExit(main())
