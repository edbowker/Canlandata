import json
from pathlib import Path

def fix_mojibake(text):
    """Fix UTF-8 text that was misread as Latin-1"""
    try:
        return text.encode('latin-1').decode('utf-8')
    except (UnicodeDecodeError, UnicodeEncodeError):
        return text  # already correct, leave it alone

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"

# --- Fix decklists.json ---
with open(DATA_DIR / 'decklists.json', 'r', encoding='utf-8') as f:
    decklists = json.load(f)

for deck in decklists:
    fixed_mainboard = {}
    for card_name, quantity in deck['mainboard'].items():
        fixed_name = fix_mojibake(card_name)
        fixed_mainboard[fixed_name] = quantity
    deck['mainboard'] = fixed_mainboard

with open(DATA_DIR / 'decklists.json', 'w', encoding='utf-8') as f:
    json.dump(decklists, f, indent=4, ensure_ascii=False)

print("Fixed decklists.json")

# --- Fix card_database.json ---
with open(DATA_DIR / 'card_database.json', 'r', encoding='utf-8') as f:
    card_db = json.load(f)

seen_oracle_ids = {}
fixed_db = {}

for card_name, card_data in card_db.items():
    oracle_id = card_data['oracle_id']
    fixed_name = fix_mojibake(card_name)

    if oracle_id not in seen_oracle_ids:
        seen_oracle_ids[oracle_id] = fixed_name
        fixed_db[fixed_name] = card_data
    else:
        existing_name = seen_oracle_ids[oracle_id]
        # Always prefer the fixed name over whatever we stored first
        if fixed_name != existing_name:
            print(f"Dropped duplicate: '{existing_name}' (keeping '{fixed_name}')")
            del fixed_db[existing_name]
            seen_oracle_ids[oracle_id] = fixed_name
            fixed_db[fixed_name] = card_data

with open(DATA_DIR / 'card_database.json', 'w', encoding='utf-8') as f:
    json.dump(fixed_db, f, indent=2, ensure_ascii=False)

print(f"Fixed card_database.json — {len(fixed_db)} cards")