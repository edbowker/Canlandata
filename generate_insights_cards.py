from collections import defaultdict
import json
import pandas as pd

with open('decklists.json', 'r') as f:
    data = json.load(f)

card_counts = defaultdict(dict)     # (card, month) -> {'plays': int, 'playrate': float}
deck_counts = defaultdict(int)      # month -> number of decks
allcards = []

# First pass: months + deck counts + collect card names
for deck in data:
    mmyy = deck['name'][:7].replace('/', '-')
    deck_counts[mmyy] += 1
    allcards.extend(deck['mainboard'].keys())

# Initialize all (card, month) pairs
allcards = set(allcards)
allmonths = deck_counts.keys()
for card in allcards:
    for month in allmonths:
        card_counts[(card, month)]['plays'] = 0
        card_counts[(card, month)]['playrate'] = 0.0

# Second pass: increment plays
for deck in data:
    mmyy = deck['name'][:7].replace('/', '-')
    for card in deck['mainboard'].keys():
        card_counts[(card, mmyy)]['plays'] += 1

# Compute playrate
for (card, month), stats in card_counts.items():
    plays = stats['plays']
    if plays > 0:
        stats['playrate'] = round(plays / deck_counts[month], 4)

# Output with new columns
rows = [
    {
        'year_month': month,
        'card': card,
        'plays': stats['plays'],
        'playrate': stats['playrate'],
    }
    for (card, month), stats in card_counts.items()
]

df = pd.DataFrame(rows)
df.to_csv('data.csv', index=False)

df_deck_counts = pd.DataFrame(deck_counts.items(), columns=['year_month', 'count'])
df_deck_counts.to_csv('deck_counts.csv', index=False)
