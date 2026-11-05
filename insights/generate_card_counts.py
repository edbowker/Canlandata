import json
import csv
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
DATA_OUT = DATA_DIR / "card_counts.csv"

# Creates table of card play counts and play rates across the full time period
# A card's denominator only counts decks from its release month onward (same
# logic as the "All Time" view on the card play rates webpage)
# Saves to card_counts.csv
# Returns nothing

def main():
    with open(DATA_DIR / "decklists.json", encoding="utf-8") as f:
        decklists = json.load(f)

    with open(DATA_DIR / "card_database.json", encoding="utf-8") as f:
        card_db = json.load(f)

    def to_month(deck):
        date = deck.get("date") or deck["name"][:10]
        return date[:7].replace("/", "-")

    deck_counts = defaultdict(int)   # "YYYY-MM" -> deck count
    card_plays = defaultdict(int)    # card -> number of decks playing it
    card_first_month = {}            # card -> earliest month it appears in the data

    for deck in decklists:
        month = to_month(deck)
        deck_counts[month] += 1
        for card in deck["mainboard"]:
            card_plays[card] += 1
            if card not in card_first_month or month < card_first_month[card]:
                card_first_month[card] = month

    all_months = sorted(deck_counts)

    rows = []
    for card, plays in card_plays.items():
        released_at = card_db.get(card, {}).get("released_at")
        release_month = released_at[:7] if released_at else None
        effective_start = release_month or card_first_month[card]

        total_decks = sum(count for month, count in deck_counts.items() if month >= effective_start)
        play_rate = round(plays / total_decks * 100, 2) if total_decks > 0 else 0.0

        rows.append((card, plays, play_rate))

    rows.sort(key=lambda row: row[1], reverse=True)

    with open(DATA_OUT, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["card_name", "plays", "play_rate"])
        writer.writerows(rows)

    print(f"Done. {len(rows)} cards saved to {DATA_OUT}")


if __name__ == "__main__":
    main()
