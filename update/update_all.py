import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from insights import generate_insights_cards
from insights import generate_insights_colors
from insights import generate_insights_sets
from insights import generate_monthly_report
from update import update_ids_lists
from update import update_card_database

print('Starting update process...')

# Check for new decks and update database
print('Checking for new decks on winners archive...')
new_deck_count = update_ids_lists.main()

# If new decks, update card database and recreate insights

print('Updating local card database...')
update_card_database.main()

print('Recreating local data files...')
generate_insights_cards.main()
generate_insights_colors.main()
generate_insights_sets.main()
generate_monthly_report.main()

