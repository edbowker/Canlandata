import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
DECKLISTS_PATH = DATA_DIR / "decklists.json"

PATTERN = re.compile(
    r'^(\d{4}/\d{2}/\d{2})\s+-\s+(.+?)\s+-\s+(.+?)\s+\((.+?)(?:,\s*(.+))?\)$'
)

with open(DECKLISTS_PATH, encoding="utf-8") as f:
    decklists = json.load(f)

matched = 0
unmatched = 0

reordered = []
for deck in decklists:
    name = deck.get("name", "")
    m = PATTERN.match(name)
    if m:
        date        = m.group(1).strip()
        deck_name   = m.group(2).strip()
        placement   = m.group(3).strip()
        event_name  = m.group(4).strip()
        winner_name = m.group(5).strip() if m.group(5) else ""
        matched += 1
    else:
        date = deck_name = placement = event_name = winner_name = ""
        unmatched += 1

    reordered.append({
        "name":         deck.get("name", ""),
        "id":           deck.get("id", ""),
        "date_created": deck.get("date_created", ""),
        "date":         date,
        "deck_name":    deck_name,
        "placement":    placement,
        "event_name":   event_name,
        "winner_name":  winner_name,
        "mainboard":    deck.get("mainboard", {}),
    })

with open(DECKLISTS_PATH, "w", encoding="utf-8") as f:
    json.dump(reordered, f, ensure_ascii=False, indent=2)

print(f"Done. {matched} matched, {unmatched} unmatched.")