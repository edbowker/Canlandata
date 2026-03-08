import requests
import json
from datetime import datetime
import os
import pandas as pd
import time
import re
from pathlib import Path

headers = {
    'User-Agent': 'Canlandata/1.0',
    'Accept': '*/*'
}
card = 'Sink into Stupor'
# Query scryfall, seacrch card name and get first result
response = requests.get(
    'https://api.scryfall.com/cards/search',
    headers=headers,
    params={
        'q': f'!"{card}"',
        'order': 'released',
        'dir': 'asc',
        'unique': 'prints'
    }
)

data = response.json()['data'][0]

for key, value in data.items():
    print(f'{key}: {value}')