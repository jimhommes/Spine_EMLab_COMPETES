#
# The main EM-Lab file for in SpineToolbox.
# Commandline arguments provide which modules are run and which aren't.
#
# Jim Hommes - 25-3-2021
#

import sys
from repository import *
from spinedb import SpineDB
from electricityspotmarket_submitbids import *
from electricityspotmarket_clear import *

# Read input database from Spine
db_url = sys.argv[1]
db = SpineDB(db_url)
db_data = db.export_data()

# Create Objects from the DB in the Repository
reps = Repository(db_data)

# Init all modules and commit structure to Spine
electricity_spot_market_submit_bids = ElectricitySpotMarketSubmitBids(reps, db)
electricity_spot_market_clear = ElectricitySpotMarketClearing(reps, db)
db.commit('Initialize all module import structures')

# Submit bids to Electricity Spot Market
electricity_spot_market_submit_bids.act()

# Clear Electricity Spot Market
electricity_spot_market_clear.act()
