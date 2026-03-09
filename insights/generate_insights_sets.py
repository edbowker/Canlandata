from collections import defaultdict
import json
import pandas as pd
from pathlib import Path

# Pathing
ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
INSIGHT_DIR = ROOT / "insights"
UPDATE_DIR = ROOT / "update"
DATA_OUT = DATA_DIR / "set_counts.csv"

with open(DATA_DIR / 'decklists.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

with open(DATA_DIR / 'card_database.json', 'r', encoding='utf-8') as f:
    card_db = json.load(f)

# Get all unique months from decklists
months = set(deck['name'][:7].replace('/', '-') for deck in data)

# Get all unique sets from card database
all_sets = sorted({card_db[card]["set_name"] for card in card_db})

# Create blank dict: set_counts[month][set] = 0
set_counts = defaultdict(lambda: defaultdict(int))

for month in months:
    month_decks = [deck for deck in data if deck['name'][:7].replace('/', '-') == month]
    
    for deck in month_decks:
        for card in deck['mainboard'].keys():
            if card in card_db:
                if 'Land' in card_db[card]['type_line']:
                    continue
                card_set = card_db[card]['set_name']
                set_counts[month][card_set] += 1

# Build output rows
rows = []
for month in months:
    for card_set in all_sets:
        rows.append({
            'mm-yy': month,
            'set': card_set,
            'count': set_counts[month][card_set]
        })

df = pd.DataFrame(rows)
df = df.sort_values(['mm-yy', 'set']).reset_index(drop=True)
df.to_csv(DATA_OUT, index=False)

print(f"Done. {len(df)} rows written to {DATA_OUT}")