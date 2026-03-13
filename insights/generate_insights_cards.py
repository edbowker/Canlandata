from collections import defaultdict
import json
import pandas as pd
from pathlib import Path

# Pathing
ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
INSIGHT_DIR = ROOT / "insights"
UPDATE_DIR = ROOT / "update"
DATA_CARDS_OUT = DATA_DIR / "data.csv"
DATA_DECKS_OUT = DATA_DIR / "deck_counts.csv"


# Create table of card play rates over time
# Saves to data.csv and deck_counts.csv
# Returns nothing
# Typically called from update_all.py

def main():
    with open(DATA_DIR / 'decklists.json', 'r', encoding='utf-8') as f:
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
    df.to_csv(DATA_CARDS_OUT, index=False)
    print(f'Saved {DATA_CARDS_OUT}')

    df_deck_counts = pd.DataFrame(deck_counts.items(), columns=['year_month', 'count'])
    df_deck_counts.to_csv(DATA_DECKS_OUT, index=False)
    print(f'Saved {DATA_DECKS_OUT}')