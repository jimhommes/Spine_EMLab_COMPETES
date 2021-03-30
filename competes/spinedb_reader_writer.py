#
# This is the Python class responsible for all reads and writes of the SpineDB.
# This is a separate file so that all import definitions are centralized.
#
# Jim Hommes - 25-3-2021
#
from repository import *
from spinedb import SpineDB


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

    def __init__(self, db_url):
        self.db_url = db_url
        self.db = SpineDB(db_url)
        self.ppdp_object_class_name = 'PowerPlantDispatchPlans'
        self.mcp_object_class_name = 'MarketClearingPoints'

    def read_db_and_create_repository(self):
        reps = Repository()
        reps.dbrw = self
        db_data = self.db.export_data()
        db_objects_to_dict(db_data, reps.energyProducers, 'EnergyProducers', EnergyProducer)
        db_objects_to_dict(db_data, reps.powerPlants, 'PowerPlants', PowerPlant)
        db_objects_to_dict(db_data, reps.substances, 'Substances', Substance)
        db_relationships_to_arr(db_data, reps.powerPlantsFuelMix, 'PowerGeneratingTechnologyFuel')
        db_objects_to_dict(db_data, reps.electricitySpotMarkets, 'ElectricitySpotMarkets', ElectricitySpotMarket)
        db_objects_to_dict(db_data, reps.powerGeneratingTechnologies, 'PowerGeneratingTechnologies',
                           PowerGeneratingTechnology)
        db_objects_to_dict(db_data, reps.load, 'ldcNLDE-hourly', HourlyLoad)
        db_objects_to_dict(db_data, reps.capacityMarkets, 'CapacityMarkets', CapacityMarket)
        return reps

    def import_object_class(self, object_class_name):
        self.import_object_classes([object_class_name])

    def import_object_classes(self, arr):
        self.db.import_object_classes(arr)

    def import_object_parameter(self, object_class, object_parameter):
        self.db.import_data({'object_parameters': [[object_class, object_parameter]]})

    def import_object_parameters(self, object_class, object_parameter_arr):
        for object_parameter in object_parameter_arr:
            self.import_object_parameter(object_class, object_parameter)

    def import_object(self, object_class, object_name):
        self.import_objects([(object_class, object_name)])

    def import_objects(self, arr_of_tuples):
        self.db.import_objects(arr_of_tuples)

    def import_object_parameter_values(self, object_class_name, object_name, arr_of_tuples):
        import_arr = [(object_class_name, object_name, i[0], i[1]) for i in arr_of_tuples]
        self.db.import_object_parameter_values(import_arr)

    def commit(self, commit_message):
        self.db.commit(commit_message)

    def init_marketclearingpoint_structure(self):
        self.import_object_class(self.mcp_object_class_name)
        self.import_object_parameters(self.mcp_object_class_name, ['Market', 'Price', 'TotalCapacity'])

    def init_powerplantdispatchplan_structure(self):
        self.import_object_class(self.ppdp_object_class_name)
        self.import_object_parameters(self.ppdp_object_class_name, ['Market', 'Price', 'Capacity', 'EnergyProducer', 'AcceptedAmount', 'Status'])
