import requests
import json
import time
from pathlib import Path

# Pathing
ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
INSIGHT_DIR = ROOT / "insights"
UPDATE_DIR = ROOT / "update"

# Go get list of all cards from decklists
with open(DATA_DIR / 'decklists.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

allcards = set([card for deck in data for card in deck['mainboard']])

# Go get (if exists) card database file
db_path = DATA_DIR / 'card_database.json'

if db_path.exists():
    with open(db_path, 'r', encoding='utf-8') as f:
        card_db = json.load(f)
else:
    card_db = {}

# For each card missing from database file, get info from Scryfall API
missing_cards = [card for card in allcards if card not in card_db]
errors = []
headers = {
    'User-Agent': 'Canlandata/1.0',
    'Accept': '*/*'
}

for i, card in enumerate(missing_cards):
    # Query scryfall, seacrch card name and get first result
    try:
        response = requests.get(
            'https://api.scryfall.com/cards/search',
            headers=headers,
            params={
                'q': f'!"{card}"',
                'order': 'released',
                'dir': 'asc',
                'unique': 'prints'
            },
            timeout=10
        )
    except requests.exceptions.ReadTimeout:
        print(f'Timed out on {card}, skipping')
        continue
    
    # Check if there is a response
    if response.status_code == 200:

        # Make sure there is data in the response
        data = response.json().get('data', [])
        if data:
            print(f'Saving data for {card}')
            data = data[0]
            card_db[card] = {}

            # Save data to dict
            try:
                # If dual faced card
                if 'card_faces' in data and data['layout'] != 'split' :
                    card_db[card]['oracle_id'] = data['oracle_id']
                    card_db[card]['mana_cost'] = data['card_faces'][0]['mana_cost']
                    card_db[card]['cmc'] = data['cmc']
                    card_db[card]['type_line'] = data['type_line']
                    card_db[card]['color_identity'] = data['color_identity']
                    if data['set_name'] == "Modern Horizons 2 Promos":
                        card_db[card]['set_name'] = "Modern Horizons 2"
                    else:
                        card_db[card]['set_name'] = data['set_name']

                # If single faced card
                else:
                    card_db[card]['oracle_id'] = data['oracle_id']
                    card_db[card]['mana_cost'] = data['mana_cost']
                    card_db[card]['cmc'] = data['cmc']
                    card_db[card]['type_line'] = data['type_line']
                    card_db[card]['color_identity'] = data['color_identity']
                    if data['set_name'] == "Modern Horizons 2 Promos":
                        card_db[card]['set_name'] = "Modern Horizons 2"
                    else:
                        card_db[card]['set_name'] = data['set_name']
                # Save after every 100 cards
                if i % 100 == 0:
                    with open(db_path, 'w') as f:
                        json.dump(card_db, f, indent=2)
                    print(f'Saved progress after {i} cards')
            
            except KeyError as e:
                print(f'Error logged on {e}')
                errors.append(f'Missing field {e} for {card}')

        else:
            print(f"No results: {card}")
    else:
        print(f"Not found: {card}")
    
    # Scryfall rate limit
    time.sleep(0.15)

# Save to card database file
with open(db_path, 'w', encoding='utf-8') as f:
    json.dump(card_db, f, indent=2, ensure_ascii=False)

print(f"Done. Database has {len(card_db)} cards.")

if len(errors) > 0:
    print('Errors below')
    for e in errors:
        print(e)