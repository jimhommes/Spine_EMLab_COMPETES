#
# This is the Python class responsible for all reads and writes of the SpineDB.
# This is a separate file so that all import definitions are centralized.
#
# Jim Hommes - 25-3-2021
#
from dependencies.repository import *
from dependencies.spinedb import SpineDB


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
        self.powerplant_dispatch_plan_classname = 'PowerPlantDispatchPlans'
        self.market_clearing_point_object_classname = 'MarketClearingPoints'

    def read_db_and_create_repository(self):
        reps = Repository()
        reps.dbrw = self
        db_data = self.db.export_data()
        db_objects_to_dict(db_data, reps.energy_producers, 'EnergyProducers', EnergyProducer)
        db_objects_to_dict(db_data, reps.power_plants, 'PowerPlants', PowerPlant)
        db_objects_to_dict(db_data, reps.substances, 'Substances', Substance)
        db_relationships_to_arr(db_data, reps.power_plants_fuel_mix, 'PowerGeneratingTechnologyFuel')
        db_objects_to_dict(db_data, reps.electricity_spot_markets, 'ElectricitySpotMarkets', ElectricitySpotMarket)
        db_objects_to_dict(db_data, reps.power_generating_technologies, 'PowerGeneratingTechnologies',
                           PowerGeneratingTechnology)
        db_objects_to_dict(db_data, reps.load, 'ldcNLDE-hourly', HourlyLoad)
        db_objects_to_dict(db_data, reps.capacity_markets, 'CapacityMarkets', CapacityMarket)

        # Interpret time series MarketClearingPoints
        for unit in [i for i in db_data['objects'] if i[0] == 'MarketClearingPoints']:
            price = 0
            market = ''
            capacity = 0
            for parameterValue in [i for i in db_data['object_parameter_values'] if i[1] == unit[1]]:
                if parameterValue[2] == 'Price':
                    price = float(parameterValue[3])
                if parameterValue[2] == 'Market':
                    market = parameterValue[3]
                if parameterValue[2] == 'TotalCapacity':
                    capacity = float(parameterValue[3])
            reps.market_clearing_points.append(MarketClearingPoint(market, price, capacity))

        # Determine current tick
        all_ticks = [int(i[4]) for i in db_data['object_parameter_values'] if i[4] != 'init']
        reps.current_tick = max(all_ticks) + 1 if len(all_ticks) > 0 else 0
        self.stage_init_alternative(reps.current_tick)

        return reps

    def stage_object_class(self, object_class_name):
        self.stage_object_classes([object_class_name])

    def stage_object_classes(self, arr):
        self.db.import_object_classes(arr)

    def stage_object_parameter(self, object_class, object_parameter):
        self.db.import_data({'object_parameters': [[object_class, object_parameter]]})

    def stage_object_parameters(self, object_class, object_parameter_arr):
        for object_parameter in object_parameter_arr:
            self.stage_object_parameter(object_class, object_parameter)

    def stage_object(self, object_class, object_name):
        self.stage_objects([(object_class, object_name)])

    def stage_objects(self, arr_of_tuples):
        self.db.import_objects(arr_of_tuples)

    def stage_object_parameter_values(self, object_class_name, object_name, arr_of_tuples, current_tick):
        import_arr = [(object_class_name, object_name, i[0], i[1], current_tick) for i in arr_of_tuples]
        self.db.import_object_parameter_values(import_arr)

    def stage_init_market_clearing_point_structure(self):
        self.stage_object_class(self.market_clearing_point_object_classname)
        self.stage_object_parameters(self.market_clearing_point_object_classname, ['Market', 'Price', 'TotalCapacity'])

    def stage_init_power_plant_dispatch_plan_structure(self):
        self.stage_object_class(self.powerplant_dispatch_plan_classname)
        self.stage_object_parameters(self.powerplant_dispatch_plan_classname,
                                     ['Market', 'Price', 'Capacity', 'EnergyProducer', 'AcceptedAmount', 'Status'])

    def stage_power_plant_dispatch_plan(self, ppdp, current_tick):
        self.stage_object(self.powerplant_dispatch_plan_classname, ppdp.plant.name)
        self.stage_object_parameter_values(self.powerplant_dispatch_plan_classname, ppdp.plant.name,
                                           [('Market', ppdp.bidding_market.name),
                                             ('Price', ppdp.price),
                                             ('Capacity', ppdp.amount),
                                             ('EnergyProducer', ppdp.bidder.name),
                                             ('AcceptedAmount', ppdp.amount),
                                             ('Status', ppdp.status)], str(current_tick))

    def stage_market_clearing_point(self, mcp, current_tick):
        object_name = 'ClearingPoint-' + str(datetime.now())
        self.stage_object(self.market_clearing_point_object_classname, object_name)
        self.stage_object_parameter_values(self.market_clearing_point_object_classname, object_name,
                                           [('Market', mcp.market),
                                             ('Price', mcp.price),
                                             ('TotalCapacity', mcp.capacity)], str(current_tick))

    def stage_init_alternative(self, current_tick):
        self.db.import_alternatives([str(current_tick)])

    def commit(self, commit_message):
        self.db.commit(commit_message)
