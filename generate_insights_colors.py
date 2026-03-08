from collections import defaultdict
import json
import pandas as pd

with open('decklists.json', 'r') as f:
    data = json.load(f)

with open('card_database.json', 'r') as f:
    card_db = json.load(f)

# Get all unique months from decklists
months = set(deck['name'][:7].replace('/', '-') for deck in data)

# Create blank dict
color_counts = defaultdict(dict)
for month in months:
    color_counts[month]['W'] = 0
    color_counts[month]['U'] = 0
    color_counts[month]['B'] = 0
    color_counts[month]['R'] = 0
    color_counts[month]['G'] = 0

for month in months:

    # Get all decks from this month
    month_decks = [deck for deck in data if deck['name'][:7].replace('/', '-') == month]
    
    # Tally pips
    for deck in month_decks:
        for card in deck['mainboard'].keys():
            cost = card_db[card]['mana_cost']
            if len(cost) > 0:
                    color_counts[month]['W'] += cost.count('W')
                    color_counts[month]['U'] += cost.count('U')
                    color_counts[month]['B'] += cost.count('B')
                    color_counts[month]['R'] += cost.count('R')
                    color_counts[month]['G'] += cost.count('G')

# Add percentages to color_counts
for month, colors in color_counts.items():
    total = sum(colors.values())
    for color in ['W', 'U', 'B', 'R', 'G']:
        color_counts[month][f'{color}_pct'] = round(colors[color] / total, 4) if total > 0 else 0

# Build output rows
rows = []
for month, colors in color_counts.items():
    for color in ['W', 'U', 'B', 'R', 'G']:
        rows.append({
            'mm-yy': month,
            'color': color,
            'count': color_counts[month][color],
            'pct': color_counts[month][f'{color}_pct']
        })

df = pd.DataFrame(rows)
df = df.sort_values(['mm-yy', 'color']).reset_index(drop=True)
df.to_csv('color_pips.csv', index=False)

print(f"Done. {len(df)} rows written to color_pips.csv")