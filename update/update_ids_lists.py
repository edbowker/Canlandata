import requests
import json
import os
import pandas as pd
import time
from pathlib import Path

# Pathing
ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
INSIGHT_DIR = ROOT / "insights"
UPDATE_DIR = ROOT / "update"

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
for page in range(1, data['totalPages']+1):
    response = requests.get(apiurl + f'&pageNumber={page}&pagesize=100', headers=headers, timeout=360)
    data = response.json()['data']

    for deck in data:
        deck_ids.append(deck['publicId'])

    time.sleep(1)

# compare against current deck_ids in decklists.json
with open(DATA_DIR / 'decklists.json', 'r') as f:
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
        response.encoding = 'utf-8'
    except:
        print(f'Couldnt Connect {deckid}')
        continue
    
    # add every card to a list (name? scryfall id?)
    cards_for_export = {}
    main = response.json()['mainboard']
    for card in main:
        cards_for_export[main[card]['card']['name']] = main[card]['quantity']

    # add list, name, and date to a json entry
    output = {'name': response.json()['name'],
              'id': deckid,
              'date_created': response.json()['createdAtUtc'],
              'mainboard': cards_for_export
    }
    data.append(output)
    print(f'Added {deckid} to decklists.json')

# save JSON
with open(DATA_DIR / 'decklists.json', 'w') as file:
    json.dump(data, file, indent=4)

print(f'Canlander archive has {len(deck_ids)} decks')
print(f'Decklist json has {len(data)} decks')