import requests
import json
import os
import re
import pandas as pd
import time
from pathlib import Path

PATTERN = re.compile(
    r'^(\d{4}/\d{2}/\d{2})\s+-\s+(.+?)\s+-\s+(.+?)\s+\((.+?)(?:,\s*(.+))?\)$'
)

# Pathing
ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
INSIGHT_DIR = ROOT / "insights"
UPDATE_DIR = ROOT / "update"

# Check for new decks on moxfield profile, update our databse with them, and return the # of new decks found.
# This is usually called from the update_all.py script

def main():
    # pull deck ids from moxfield
    apiurl = 'https://api2.moxfield.com/v2/decks/search?includePinned=true&showIllegal=true&authorUserNames=CanlanderWinnersArchive'
    apikey = os.getenv('MOXFIELD_USER_AGENT')

    headers = {
            "User-Agent": apikey,
            "Accept": "application/json"
        }

    response = requests.get(apiurl + '&pageNumber=1&pagesize=100', headers=headers, timeout=360)
    data = response.json()

    time.sleep(1)

    deck_ids = []
    totalPages = data['totalPages']
    for page in range(1, totalPages+1):
        response = requests.get(apiurl + f'&pageNumber={page}&pagesize=100', headers=headers, timeout=360)
        data = response.json()['data']

        for deck in data:
            deck_ids.append(deck['publicId'])

        print(f'Page {page}/{totalPages} done')
        time.sleep(2)

    # compare against current deck_ids in decklists.json
    with open(DATA_DIR / 'decklists.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    current_ids = [deck['id'] for deck in data]

    # set aside new ids
    update_ids = list(set(deck_ids) - set(current_ids))

    print(f'{len(update_ids)} new decks found')

    # rewrite deck_ids.csv
    df = pd.DataFrame(deck_ids)
    df.to_csv(DATA_DIR / 'deck_ids.csv', index=False, header=None)

    # for each new id
    for deckid in update_ids:

        # load deck id from moxfield
        time.sleep(1)
        try:
            response = requests.get('https://api.moxfield.com/v2/decks/all/' + deckid, headers=headers, timeout=360)
        except:
            print(f'Couldnt Connect {deckid}')
            continue
        
        # add every card to a list (name? scryfall id?)
        cards_for_export = {}
        try:
            main = response.json()['mainboard']
        except:
            print(f'Couldnt access main[mainboard] for id {deckid}')
        for card in main:
            cards_for_export[main[card]['card']['name']] = main[card]['quantity']

        # add list, name, and date to a json entry
        deck_name = response.json()['name']
        m = PATTERN.match(deck_name)
        output = {
            'name':         deck_name,
            'id':           deckid,
            'date_created': response.json()['createdAtUtc'],
            'date':         m.group(1).strip() if m else "",
            'deck_name':    m.group(2).strip() if m else "",
            'placement':    m.group(3).strip() if m else "",
            'event_name':   m.group(4).strip() if m else "",
            'winner_name':  m.group(5).strip() if m and m.group(5) else "",
            'mainboard':    cards_for_export,
        }
        data.append(output)
        print(f'Added {deckid} to decklists.json')

    # save JSON
    with open(DATA_DIR / 'decklists.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    print(f'Canlander archive has {len(deck_ids)} decks')
    print(f'Decklist database has {len(data)} decks')

    return len(update_ids)
