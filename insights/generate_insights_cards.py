from pathlib import Path
from collections import defaultdict
import json
import csv

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
CARD_INDEX_OUT = DATA_DIR / "card_index.json"
DECK_DATES_OUT = DATA_DIR / "deck_dates.json"
DECK_COUNTS_OUT = DATA_DIR / "deck_counts.csv"


def main():
    with open(DATA_DIR / "decklists.json", encoding="utf-8") as f:
        decklists = json.load(f)

    card_index = defaultdict(list)  # card name → [deck_ids]
    deck_dates = {}                 # deck_id → "YYYY-MM"
    deck_counts = defaultdict(int)  # "YYYY-MM" → deck count

    for deck in decklists:
        deck_id = deck["id"]
        date = deck["name"][:7].replace("/", "-")

        deck_dates[deck_id] = date
        deck_counts[date] += 1

        for card in deck["mainboard"]:
            card_index[card].append(deck_id)

    with open(CARD_INDEX_OUT, "w", encoding="utf-8") as f:
        json.dump(dict(card_index), f, ensure_ascii=False, indent=2)

    with open(DECK_DATES_OUT, "w", encoding="utf-8") as f:
        json.dump(deck_dates, f, ensure_ascii=False, indent=2)

    with open(DECK_COUNTS_OUT, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["year_month", "count"])
        for month, count in sorted(deck_counts.items()):
            writer.writerow([month, count])

    print(f"Done. {len(card_index)} cards saved to {CARD_INDEX_OUT}")
    print(f"Done. {len(deck_dates)} decks saved to {DECK_DATES_OUT}")
    print(f"Done. {len(deck_counts)} months saved to {DECK_COUNTS_OUT}")
