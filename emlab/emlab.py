#
# The main EM-Lab file for in SpineToolbox.
# Commandline arguments provide which modules are run and which aren't.
#
# Jim Hommes - 25-3-2021
#

import sys
from electricityspotmarket_submitbids import *
from electricityspotmarket_clear import *
from spinedb_reader_writer import *

run_capacity_market = False
run_electricity_spot_market = False

# Loop over provided arguments and select modules
for arg in sys.argv[2:]:
    if arg == 'run_capacity_market':
        run_electricity_spot_market = True
        run_capacity_market = True
    if arg == 'run_electricity_spot_market':
        run_electricity_spot_market = True

# Read input database from Spine
db_url = sys.argv[1]

# Create Objects from the DB in the Repository
spinedb_reader_writer = SpineDBReaderWriter(db_url)
reps = spinedb_reader_writer.read_db_and_create_repository()

# Init all modules and commit structure to Spine
electricity_spot_market_submit_bids = ElectricitySpotMarketSubmitBids(reps)
electricity_spot_market_clear = ElectricitySpotMarketClearing(reps)
spinedb_reader_writer.commit('Initialize all module import structures')

# Submit bids to Electricity Spot Market
if run_electricity_spot_market:
    electricity_spot_market_submit_bids.act()

# Clear Electricity Spot Market
if run_electricity_spot_market:
    electricity_spot_market_clear.act()
