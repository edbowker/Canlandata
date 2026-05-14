import json, re
from pathlib import Path

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"

PATTERN = re.compile(
    r'^(\d{4}/\d{2}/\d{2})\s+-\s+(.+?)\s+-\s+(.+?)\s+\((.+?)(?:,\s*(.+))?\)$'
)

with open(DATA_DIR / "decklists.json", encoding="utf-8") as f:
    decklists = json.load(f)

fixed = 0
for deck in decklists:
    if "date" not in deck:
        m = PATTERN.match(deck.get("name", ""))
        deck["date"]        = m.group(1).strip() if m else ""
        deck["deck_name"]   = m.group(2).strip() if m else ""
        deck["placement"]   = m.group(3).strip() if m else ""
        deck["event_name"]  = m.group(4).strip() if m else ""
        deck["winner_name"] = m.group(5).strip() if m and m.group(5) else ""
        # move mainboard to end
        mb = deck.pop("mainboard")
        deck["mainboard"] = mb
        fixed += 1

with open(DATA_DIR / "decklists.json", "w", encoding="utf-8") as f:
    json.dump(decklists, f, ensure_ascii=False, indent=2)

print(f"Fixed {fixed} entries")