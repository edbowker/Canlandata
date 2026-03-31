import json
from pathlib import Path

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"

SUSPICIOUS = ['Ã', '\u00c3', 'Â', '\u00c2']

# --- Check decklists.json ---
with open(DATA_DIR / 'decklists.json', 'r', encoding='utf-8') as f:
    decklists = json.load(f)

decklist_issues = []
for deck in decklists:
    for card_name in deck['mainboard']:
        if any(s in card_name for s in SUSPICIOUS):
            decklist_issues.append(f"  [{deck['id']}] {card_name}")

print(f"decklists.json: {len(decklist_issues)} problematic card names")
for issue in decklist_issues:
    print(issue)

# --- Check card_database.json ---
with open(DATA_DIR / 'card_database.json', 'r', encoding='utf-8') as f:
    card_db = json.load(f)

db_issues = []
for card_name in card_db:
    if any(s in card_name for s in SUSPICIOUS):
        db_issues.append(f"  {card_name}")

print(f"\ncard_database.json: {len(db_issues)} problematic card names")
for issue in db_issues:
    print(issue)

print("\nDone.")