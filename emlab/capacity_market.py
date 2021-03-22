#
# The Capacity Market recreated from EM-Lab.
#
# Jim Hommes - 17-3-2021
#

import sys
import random
import json
from repository import *
from spinedb import SpineDB
from datetime import datetime

# Input DB
db_url = sys.argv[1]
db = SpineDB(db_url)
db_data = db.export_data()

# Create Objects from the DB Data in the Repository
reps = Repository(db_data)

# Create the DB Object structure for the PPDPs
db.import_object_classes(['PowerPlantDispatchPlans'])
db.import_data({'object_parameters': [['PowerPlantDispatchPlans', 'Market']]})
db.import_data({'object_parameters': [['PowerPlantDispatchPlans', 'Price']]})
db.import_data({'object_parameters': [['PowerPlantDispatchPlans', 'Capacity']]})
db.import_data({'object_parameters': [['PowerPlantDispatchPlans', 'EnergyProducer']]})

# For every energy producer we will submit bids to the Capacity Market
for energyProducer in reps.energyProducers.values():
    market = reps.electricitySpotMarkets[energyProducer.parameters['investorMarket']]

    # For every plant owned by energyProducer
    for powerPlant in reps.get_powerplants_by_owner(energyProducer.name):
        db.import_objects([('PowerPlantDispatchPlans', powerPlant.name)])

        # Calculate marginal cost mc
        #   fuelConsumptionPerMWhElectricityProduced = 3600 / (pp.efficiency * ss.energydensity)
        #   lastKnownFuelPrice
        substances = reps.get_substances_by_powerplant(powerPlant.name)
        if len(substances) > 0:         # Only done for 1 substance atm
            mc = 3600 / (float(powerPlant.parameters['Efficiency']) * float(substances[0].parameters['energyDensity']))
            capacity = int(powerPlant.parameters['Capacity'])
            reps.create_powerplant_dispatch_plan(powerPlant, energyProducer, market, capacity, mc)

            db.import_object_parameter_values([('PowerPlantDispatchPlans', powerPlant.name, 'Market', market.name),
                                               ('PowerPlantDispatchPlans', powerPlant.name, 'Price', mc),
                                               ('PowerPlantDispatchPlans', powerPlant.name, 'Capacity', capacity),
                                               ('PowerPlantDispatchPlans', powerPlant.name, 'EnergyProducer',
                                                energyProducer.name)])

db.commit('EM-Lab Capacity Market: Submit Bids: ' + str(datetime.now()))

# Create the DB Object structure for Clearing Prices
db.import_object_classes(['MarketClearingPoints'])
db.import_data({'object_parameters': [['MarketClearingPoints', 'Market']]})
db.import_data({'object_parameters': [['MarketClearingPoints', 'Price']]})
db.import_data({'object_parameters': [['MarketClearingPoints', 'TotalCapacity']]})

# Calculate and submit Market Clearing Price
peak_load = max(json.loads(reps.load['NL'].parameters['ldc'].to_database())['data'].values())
for market in reps.electricitySpotMarkets.values():
    sorted_ppdp = reps.get_sorted_dispatch_plans_by_market(market.name)
    clearing_price = 0
    total_load = 0
    for ppdp in sorted_ppdp:
        if total_load < peak_load:
            total_load += ppdp.amount
            clearing_price = ppdp.price

    db.import_objects([('MarketClearingPoints', 'ClearingPoint')])
    db.import_object_parameter_values([('MarketClearingPoints', 'ClearingPoint', 'Market', market.name),
                                       ('MarketClearingPoints', 'ClearingPoint', 'Price', clearing_price),
                                       ('MarketClearingPoints', 'ClearingPoint', 'TotalCapacity', total_load)])

db.commit('EM-Lab Capacity Market: Submit Clearing Point: ' + str(datetime.now()))
