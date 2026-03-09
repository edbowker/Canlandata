import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

with open(DATA_DIR / 'decklists.json', 'r', encoding='utf-8') as f:
    decklists = json.load(f)
print('running...')
for deck in decklists:
    for card_name in deck['mainboard']:
        if 'Ã' in card_name:
            print(card_name)
            break

print('done')