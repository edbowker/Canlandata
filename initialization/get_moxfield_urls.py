import requests
import json
from datetime import datetime
import os
import pandas as pd
import time
import re
from pathlib import Path

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


df = pd.DataFrame(deck_ids)
df.to_csv('deck_ids.csv', index=False, header=None)