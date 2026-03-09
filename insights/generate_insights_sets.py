import json
import pandas as pd
from pathlib import Path

# Pathing
ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
DATA_OUT = DATA_DIR / "set_apps.csv"

with open(DATA_DIR / 'decklists.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

with open(DATA_DIR / 'card_database.json', 'r', encoding='utf-8') as f:
    card_db = json.load(f)

rows = []

for deck in data:
    month = deck['name'][:7].replace('/', '-')
    for card in deck['mainboard'].keys():
        if card in card_db:
            if 'Land' in card_db[card]['type_line']:
                continue
            rows.append({
                'mm-yy': month,
                'card_name': card,
                'set': card_db[card]['set_name']
            })

df = pd.DataFrame(rows)

# Aggregate: one row per month+card, with play count
df = df.groupby(['mm-yy', 'card_name', 'set']).size().reset_index(name='plays')

df = df.sort_values(['mm-yy', 'set']).reset_index(drop=True)
df.to_csv(DATA_OUT, index=False)

print(f"Done. {len(df)} rows written to {DATA_OUT}")