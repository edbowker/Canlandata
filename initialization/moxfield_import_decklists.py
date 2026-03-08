import requests
import json
from datetime import datetime
import os
import pandas as pd
import time
import re
from pathlib import Path

# api info
apiurl = 'https://api.moxfield.com/v2/decks/all/'
apikey = os.getenv('MOXFIELD_USER_AGENT')

headers = {
    "User-Agent": apikey,
    "Accept": "application/json"
}

# Load csv with deck ids
deck_ids = pd.read_csv('deck_ids.csv', header=None)

# output
json_out = []

# Iterate over deck ids
count = 0
for deckid in deck_ids[0]:

    # load deck id from moxfield
    time.sleep(1)
    try:
        response = requests.get(apiurl + deckid, headers=headers, timeout=360)
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
    json_out.append(output)
    count += 1
    if count % 10 == 0:
        print(f'{count} done')


# save JSON
with open('decklists.json', 'w') as file:
    json.dump(json_out, file, indent=4)