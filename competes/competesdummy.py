#
# Dummy file to simulate a COMPETES output.
# Just generates random numbers and adds this to the SpineDB.
#
# Jim Hommes - 17-3-2021
#

import sys
import random
from datetime import datetime
from spinedb import SpineDB
from emlab.repository import *
from emlab.spinedb_reader_writer import *
from electricityspotmarket import *

# Input DB
db_url = sys.argv[1]
spinedbrw = SpineDBReaderWriter(db_url)
reps = spinedbrw.read_db_and_create_repository()

electricity_spot_market_submit_bids = ElectricitySpotMarketSubmitBids(reps)
electricity_spot_market_clear = ElectricitySpotMarketClearing(reps)

electricity_spot_market_submit_bids.act()
electricity_spot_market_clear.act()
