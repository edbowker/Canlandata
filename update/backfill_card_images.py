import requests
import json
import gzip
from pathlib import Path

# Pathing
ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
INSIGHT_DIR = ROOT / "insights"
UPDATE_DIR = ROOT / "update"


# One-time backfill: add 'image_url' to every card already in card_database.json.
# Uses Scryfall's bulk "Oracle Cards" file (one card object per oracle_id, matching
# how we identify cards) so we do a single download and join locally instead of
# making per-card API calls. Run manually once, not from update_all.py.

headers = {
    'User-Agent': 'Canlandata/1.0',
    'Accept': '*/*'
}


def get_image_url(card):
    # Normal-size image lives on the card, or on the first face for multi-faced cards
    image_uris = card.get('image_uris')
    if image_uris and image_uris.get('normal'):
        return image_uris['normal']
    for face in card.get('card_faces', []):
        face_uris = face.get('image_uris')
        if face_uris and face_uris.get('normal'):
            return face_uris['normal']
    return None


def main():
    db_path = DATA_DIR / 'card_database.json'

    with open(db_path, 'r', encoding='utf-8') as f:
        card_db = json.load(f)

    # Find the Oracle Cards bulk file and download it once
    print('Fetching Scryfall bulk data listing...')
    response = requests.get(
        'https://api.scryfall.com/bulk-data/oracle_cards',
        headers=headers,
        timeout=10
    )
    download_uri = response.json()['jsonl_download_uri']

    print(f'Downloading Oracle Cards bulk file from {download_uri}')
    bulk_response = requests.get(download_uri, headers=headers, timeout=120)
    lines = gzip.decompress(bulk_response.content).splitlines()

    # Build oracle_id -> normal image url lookup
    images_by_oracle_id = {}
    for line in lines:
        card = json.loads(line)
        images_by_oracle_id[card['oracle_id']] = get_image_url(card)

    print(f'Loaded {len(images_by_oracle_id)} cards from bulk file.')

    errors = []
    updated = 0
    for i, (card, info) in enumerate(card_db.items()):
        image_url = images_by_oracle_id.get(info.get('oracle_id'))

        if image_url:
            info['image_url'] = image_url
            updated += 1
        else:
            errors.append(f'No image found for {card}')

        # Save after every 100 cards
        if i % 100 == 0:
            with open(db_path, 'w', encoding='utf-8') as f:
                json.dump(card_db, f, indent=2, ensure_ascii=False)
            print(f'Saved progress after {i} cards')

    # Save to card database file
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(card_db, f, indent=2, ensure_ascii=False)

    print(f'Done. Backfilled image_url for {updated} of {len(card_db)} cards.')

    if len(errors) > 0:
        print('Errors below')
        for e in errors:
            print(e)


if __name__ == '__main__':
    main()
