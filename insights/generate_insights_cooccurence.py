from pathlib import Path
import json
from collections import defaultdict

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
DATA_CO_OUT = DATA_DIR / "co_occurrence_index.json"
DATA_DATES_OUT = DATA_DIR / "deck_dates.json"

def main():
    with open(DATA_DIR / "decklists.json", encoding="utf-8") as f:
        decklists = json.load(f)

    index = defaultdict(list)
    deck_dates = {}

    for deck in decklists:
        deck_id = deck["id"]
        date = deck["name"][:7].replace("/", "-")
        deck_dates[deck_id] = date

        for card in deck["mainboard"]:
            index[card].append(deck_id)

    with open(DATA_CO_OUT, "w", encoding="utf-8") as f:
        json.dump(dict(index), f, ensure_ascii=False, indent=2)

    with open(DATA_DATES_OUT, "w", encoding="utf-8") as f:
        json.dump(deck_dates, f, ensure_ascii=False, indent=2)

    print(f"Done. {len(index)} rows written to {DATA_CO_OUT}")
    print(f"Done. {len(deck_dates)} rows written to {DATA_DATES_OUT}")
