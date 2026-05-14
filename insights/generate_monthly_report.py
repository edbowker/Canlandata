import json
import csv
from pathlib import Path
from collections import defaultdict

ROOT       = Path(__file__).parent.parent
DATA_DIR   = ROOT / "data"
INSIGHT_DIR = ROOT / "insights"

TOP_N_MOVERS = 5

# ── Load data ──────────────────────────────────────────────────────────────

with open(DATA_DIR / "decklists.json", encoding="utf-8") as f:
    decklists = json.load(f)

with open(DATA_DIR / "card_index.json", encoding="utf-8") as f:
    card_index = json.load(f)
# Expected schema: { "Card Name": ["deck_id", ...] }

deck_counts = {}
with open(DATA_DIR / "deck_counts.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        deck_counts[row["year_month"]] = int(row["count"])
# Expected columns: year_month (YYYY-MM), count

# ── Helpers ────────────────────────────────────────────────────────────────

def to_month_key(date_str):
    """YYYY/MM/DD -> YYYY-MM"""
    return date_str[:7].replace("/", "-")

def play_rate(card, month):
    count = month_card_appearances.get(month, {}).get(card, 0)
    denom = deck_counts.get(month, 0)
    return round(count / denom * 100, 1) if denom > 0 else 0.0

# ── Pre-build lookups ──────────────────────────────────────────────────────

# month -> list of decklists
month_decks = defaultdict(list)
for deck in decklists:
    if deck.get("date"):
        month_decks[to_month_key(deck["date"])].append(deck)

# deck_id -> month, built from decklists
deck_id_to_month = {}
for deck in decklists:
    if deck.get("id") and deck.get("date"):
        deck_id_to_month[deck["id"]] = to_month_key(deck["date"])

# month -> { card: count }, derived by joining card_index deck_ids against dates
# card_index schema: { "Card Name": ["deck_id", ...] }
month_card_appearances = defaultdict(lambda: defaultdict(int))
for card, deck_ids in card_index.items():
    for deck_id in deck_ids:
        month = deck_id_to_month.get(deck_id)
        if month:
            month_card_appearances[month][card] += 1

# card -> first month it appeared
card_first_month = {}
for card, deck_ids in card_index.items():
    months = {deck_id_to_month[d] for d in deck_ids if d in deck_id_to_month}
    if months:
        card_first_month[card] = sorted(months)[0]

# month -> card -> [display strings] for debut deck expansion
month_card_decks = defaultdict(lambda: defaultdict(list))
for deck in decklists:
    if not deck.get("date") or not deck.get("mainboard"):
        continue
    mk      = to_month_key(deck["date"])
    winner  = deck.get("winner_name", "")
    dname   = deck.get("deck_name") or deck.get("name", "")
    label   = f"{winner} \u2013 {dname}" if winner else dname
    for card in deck["mainboard"]:
        month_card_decks[mk][card].append(label)

# ── Build report ───────────────────────────────────────────────────────────

all_months = sorted(set(list(deck_counts.keys()) + list(month_decks.keys())))
report = {}

for i, month in enumerate(all_months):
    prev = all_months[i - 1] if i > 0 else None

    # Stat chips
    deck_count  = deck_counts.get(month, 0)
    prev_count  = deck_counts.get(prev, 0) if prev else None
    deck_delta  = (deck_count - prev_count) if prev_count is not None else None

    this_decks  = month_decks.get(month, [])
    prev_decks  = month_decks.get(prev, []) if prev else []

    def event_set(decks):
        return {(d["date"], d["event_name"]) for d in decks
                if d.get("date") and d.get("event_name")}

    event_count = len(event_set(this_decks))
    event_delta = (event_count - len(event_set(prev_decks))) if prev else None

    this_cards   = month_card_appearances.get(month, {})
    prev_cards   = month_card_appearances.get(prev, {}) if prev else {}
    unique_cards = sum(1 for c in this_cards if this_cards[c] > 0)
    unique_delta = (unique_cards - sum(1 for c in prev_cards if prev_cards[c] > 0)) if prev else None

    # Rising / Falling
    movers = []
    if prev:
        all_cards = set(this_cards) | set(prev_cards)
        for card in all_cards:
            curr_rate = play_rate(card, month)
            prev_rate = play_rate(card, prev)
            delta = round(curr_rate - prev_rate, 1)
            if delta != 0:
                movers.append({
                    "card":      card,
                    "prev_rate": prev_rate,
                    "curr_rate": curr_rate,
                    "delta":     delta,
                })
        movers.sort(key=lambda x: x["delta"])

    falling = movers[:TOP_N_MOVERS]
    rising  = list(reversed(movers))[:TOP_N_MOVERS]

    # Card debuts
    debuts = []
    for card, first_month in card_first_month.items():
        if first_month == month:
            decks_featuring = month_card_decks[month].get(card, [])
            debuts.append({
                "card":       card,
                "deck_count": len(decks_featuring),
                "decks":      decks_featuring,
            })
    debuts.sort(key=lambda x: x["deck_count"], reverse=True)

    # Event winners
    winners = [
        {
            "winner_name": d.get("winner_name", ""),
            "placement":   d.get("placement", ""),
            "deck_name":   d.get("deck_name", ""),
            "event_name":  d.get("event_name", ""),
            "date":        d.get("date", ""),
        }
        for d in sorted(this_decks, key=lambda d: d.get("date", ""))
        if d.get("placement") or d.get("winner_name")
    ]

    report[month] = {
        "month":        month,
        "event_count":  event_count,
        "event_delta":  event_delta,
        "deck_count":   deck_count,
        "deck_delta":   deck_delta,
        "unique_cards": unique_cards,
        "unique_delta": unique_delta,
        "rising":       rising,
        "falling":      falling,
        "debuts":       debuts,
        "winners":      winners,
    }

DATA_DIR.mkdir(exist_ok=True)
out = DATA_DIR / "monthly_report.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(f"Written {len(report)} months to {out}")