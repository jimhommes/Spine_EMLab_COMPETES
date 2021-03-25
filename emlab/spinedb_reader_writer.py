#
# This is the Python class responsible for all reads and writes of the SpineDB.
# This is a separate file so that all import definitions are centralized.
#
# Jim Hommes - 25-3-2021
#
from repository import *


# Common function to read a SpineDB entry to a Python dict with {object_class_name: class_to_create}
# class_to_create should inherit ImportObject
# All parameters are then added to ImportObject.parameters
def db_objects_to_dict(db_data, to_dict, object_class_name, class_to_create):
    for unit in [i for i in db_data['objects'] if i[0] == object_class_name]:
        to_dict[unit[1]] = class_to_create(unit)

    for unit in to_dict.values():
        for parameterValue in [i for i in db_data['object_parameter_values'] if i[1] == unit.name]:
            unit.add_parameter_value(parameterValue)


# Function used to translate SpineDB relationships to an array of tuples
def db_relationships_to_arr(db_data, to_arr, relationship_class_name):
    for unit in [i for i in db_data['relationships'] if i[0] == relationship_class_name]:
        to_arr.append((unit[1][0], unit[1][1]))


class SpineDBReaderWriter:

    def __init__(self, db):
        self.db = db

    def read_db_and_create_repository(self):
        reps = Repository()
        db_data = self.db.export_data()
        db_objects_to_dict(db_data, reps.energyProducers, 'EnergyProducers', EnergyProducer)
        db_objects_to_dict(db_data, reps.powerPlants, 'PowerPlants', PowerPlant)
        db_objects_to_dict(db_data, reps.substances, 'Substances', Substance)
        db_relationships_to_arr(db_data, reps.powerPlantsFuelMix, 'PowerGeneratingTechnologyFuel')
        db_objects_to_dict(db_data, reps.electricitySpotMarkets, 'ElectricitySpotMarkets', ElectricitySpotMarket)
        db_objects_to_dict(db_data, reps.powerGeneratingTechnologies, 'PowerGeneratingTechnologies',
                           PowerGeneratingTechnology)
        db_objects_to_dict(db_data, reps.load, 'ldcNLDE-hourly', HourlyLoad)
        return reps
