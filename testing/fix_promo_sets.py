import requests
import json
import time
from pathlib import Path

# Pathing
ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"

def get_earliest_nonpromo(card_name, headers):
    """Query Scryfall and return the earliest non-promo printing's set_name and released_at.
    Returns (set_name, released_at) or (None, None) on failure."""
    for attempt in range(3):
        try:
            response = requests.get(
                'https://api.scryfall.com/cards/search',
                headers=headers,
                params={
                    'q': f'!"{card_name}"',
                    'order': 'released',
                    'dir': 'asc',
                    'unique': 'prints',
                },
                timeout=10
            )
        except requests.exceptions.ReadTimeout:
            print(f'  Timed out on {card_name}, skipping')
            return None, None

        if response.status_code == 429:
            wait = 5 * (attempt + 1)
            print(f'  Rate limited (429), waiting {wait}s before retry...')
            time.sleep(wait)
            continue

        if response.status_code != 200:
            print(f'  HTTP {response.status_code} for: {card_name}')
            return None, None

        printings = response.json().get('data', [])
        if not printings:
            print(f'  Empty data for: {card_name}')
            return None, None

        for printing in printings:
            if not printing.get('promo', False):
                set_name = printing['set_name']
                if set_name == 'Modern Horizons 2 Promos':
                    set_name = 'Modern Horizons 2'
                return set_name, printing['released_at']

        print(f'  All printings are promo for: {card_name}')
        return None, None

    print(f'  Failed after 3 attempts (rate limited): {card_name}')
    return None, None


def main():
    db_path = DATA_DIR / 'card_database.json'

    with open(db_path, 'r', encoding='utf-8') as f:
        card_db = json.load(f)

    headers = {
        'User-Agent': 'Canlandata/1.0',
        'Accept': '*/*'
    }

    updated = []
    errors = []
    total = len(card_db)

    for i, (card, entry) in enumerate(card_db.items()):
        print(f'[{i+1}/{total}] Checking {card}')

        new_set, new_released = get_earliest_nonpromo(card, headers)

        if new_set is None:
            errors.append(card)
            time.sleep(0.5)
            continue

        old_set = entry.get('set_name')
        old_released = entry.get('released_at')

        if new_set != old_set or new_released != old_released:
            print(f'  Updating {card}: [{old_set} | {old_released}] -> [{new_set} | {new_released}]')
            card_db[card]['set_name'] = new_set
            card_db[card]['released_at'] = new_released
            updated.append(card)

        # Save progress every 100 cards
        if (i + 1) % 100 == 0:
            with open(db_path, 'w', encoding='utf-8') as f:
                json.dump(card_db, f, indent=2, ensure_ascii=False)
            print(f'  -- Progress saved ({i+1} cards checked, {len(updated)} updated so far) --')

        time.sleep(0.5)

    # Final save
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(card_db, f, indent=2, ensure_ascii=False)

    print(f'\nDone. Checked {total} cards.')
    print(f'Updated {len(updated)} cards:')
    for card in updated:
        print(f'  {card}')

    if errors:
        print(f'\nFailed to fetch {len(errors)} cards:')
        for card in errors:
            print(f'  {card}')


main()