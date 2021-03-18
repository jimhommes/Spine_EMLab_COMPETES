#
# The Capacity Market recreated from EM-Lab.
#
# Jim Hommes - 17-3-2021
#

import sys
import random
from repository import *
from spinedb import SpineDB

# Input DB
db_url = sys.argv[1]
db = SpineDB(db_url)
db_data = db.export_data()

# Create Objects from the DB Data in the Repository
reps = Repository(db_data)

# For every energy producer we will submit bids to the Capacity Market
for energyProducer in reps.energyProducers.values():
    market = reps.electricitySpotMarkets[energyProducer.parameters['investorMarket']]

    # For every plant owned by energyProducer
    for powerPlant in reps.get_powerplants_by_owner(energyProducer.name):
        # Calculate marginal cost mc
        #   fuelConsumptionPerMWhElectricityProduced = 3600 / (pp.efficiency * ss.energydensity)
        #   lastKnownFuelPrice
        substances = reps.get_substances_by_powerplant(powerPlant.name)
        if len(substances) > 0:         # Only done for 1 substance atm
            mc = 3600 / (float(powerPlant.parameters['Efficiency']) * float(substances[0].parameters['energyDensity']))
            capacity = int(powerPlant.parameters['Capacity'])
            reps.create_powerplant_dispatch_plan(powerPlant, energyProducer, market, capacity, mc)

