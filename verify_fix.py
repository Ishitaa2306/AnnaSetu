"""Verify SQL fix and syntax"""
import ast

for f in ['tools.py', 'app.py']:
    with open(f, 'r', encoding='utf-8') as fh:
        src = fh.read()
    ast.parse(src)
    print(f'{f}: syntax OK')

import tools as t
donations = t.get_all_donations(limit=3)
has_name = "donor_name" in (donations[0] if donations else {})
print(f'get_all_donations: OK ({len(donations)} rows, donor_name present: {has_name})')

matches = t.get_matches_with_details()
print(f'get_matches_with_details: OK ({len(matches)} rows)')

import database as db
db.execute_query('SELECT 1 AS ok')
print('DB connection: OK')
print('All checks passed.')
