#
# The Capacity Market recreated from EM-Lab.
#
# Jim Hommes - 17-3-2021
#

import sys
import random
from spinedb import SpineDB

# Input DB
db_url = sys.argv[1]
db = SpineDB(db_url)
db_data = db.export_data()


class EnergyProducer:
    def __init__(self, import_obj):
        self.name = import_obj[1]
        self.parameters = {}

    def add_parameter_value(self, import_obj):
        self.parameters[import_obj[2]] = import_obj[3]


class PowerPlant:
    def __init__(self, import_obj):
        self.name = import_obj[1]
        self.parameters = {}

    def add_parameter_value(self, import_obj):
        self.parameters[import_obj[2]] = import_obj[3]


energyProducers = []
powerPlants = []

for energyProducer in [i for i in db_data['objects'] if i[0] == 'EnergyProducers']:
    energyProducers.append(EnergyProducer(energyProducer))

for energyProducer in energyProducers:
    for parameterValue in [i for i in db_data['object_parameter_values'] if i[1] == energyProducer.name]:
        energyProducer.add_parameter_value(parameterValue)

for powerPlant in [i for i in db_data['objects'] if i[0] == 'PowerPlants']:
    powerPlants.append(PowerPlant(powerPlant))

for powerPlant in powerPlants:
    for parameterValue in [i for i in db_data['object_parameter_values'] if i[1] == powerPlant.name]:
        powerPlant.add_parameter_value(parameterValue)



