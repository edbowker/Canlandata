"""
get_current_points.py

Reads the points change history CSV and outputs the current points value
for every card on the points list (i.e. cards whose most recent value > 0).

Input:  points_change_history.csv  (columns: date, Card, Old Value, New Value)
Output: prints a sorted table; optionally writes current_points.csv
"""

import pandas as pd
from pathlib import Path
import json

# ── Paths ──────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
INPUT_FILE  = DATA_DIR / "points_change_history.csv"
OUTPUT_FILE = DATA_DIR / "current_points.csv" 

# ── Load ───────────────────────────────────────────────────────────────────────
df = pd.read_csv(INPUT_FILE, encoding="utf-8")

# Rename the unnamed date column
df.columns = ["Date", "Card", "Old Value", "New Value"]

# Parse dates so sorting is chronological, not lexicographic
df["Date"] = pd.to_datetime(df["Date"])

# ── Derive current values ──────────────────────────────────────────────────────
# Sort oldest → newest, then keep only the last row per card.
# That last row's New Value is the card's current points value.
df_sorted = df.sort_values("Date")
current = (
    df_sorted
    .groupby("Card", as_index=False)
    .last()                          # last change event per card
    [["Card", "New Value", "Date"]]
    .rename(columns={"New Value": "Points", "Date": "Last Updated"})
)

# Cards with a current value of 0 have been removed from the points list
on_list  = current[current["Points"] > 0].copy()
off_list = current[current["Points"] == 0].copy()

# ── Cross-check against card database ─────────────────────────────────────────
with open(DATA_DIR / "card_database.json", encoding="utf-8") as f:
    card_db = json.load(f)

db_names = set(card_db.keys())

missing_from_db = on_list[~on_list["Card"].isin(db_names)]["Card"].tolist()

if missing_from_db:
    print(f"\nWARNING: {len(missing_from_db)} pointed card(s) not found in card_database.json:")
    for card in missing_from_db:
        print(f"  - {card}")
else:
    print("\nAll pointed cards found in card_database.json.")


# Sort by points descending, then alphabetically
on_list = on_list.sort_values(["Points", "Card"], ascending=[False, True])

# ── Display ────────────────────────────────────────────────────────────────────
print(f"{'Card':<30} {'Points':>6}  {'Last Updated'}")
print("-" * 55)
for _, row in on_list.iterrows():
    print(f"{row['Card']:<30} {row['Points']:>6}  {row['Last Updated'].strftime('%Y-%m-%d')}")

print()
print(f"{len(on_list)} cards currently on the points list.")

if off_list.shape[0]:
    print(f"{off_list.shape[0]} cards were removed from the list (value returned to 0):")
    print(", ".join(sorted(off_list["Card"].tolist())))

# ── Write CSV ──────────────────────────────────────────────────────────────────
if OUTPUT_FILE:
    on_list.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
    print(f"\nSaved to {OUTPUT_FILE}")