def db_objects_to_dict(db_data, to_dict, object_class_name, class_to_create):
    for unit in [i for i in db_data['objects'] if i[0] == object_class_name]:
        to_dict[unit[1]] = class_to_create(unit)

    for unit in to_dict.values():
        for parameterValue in [i for i in db_data['object_parameter_values'] if i[1] == unit.name]:
            unit.add_parameter_value(parameterValue)


def db_relationships_to_arr(db_data, to_arr, relationship_class_name):
    for unit in [i for i in db_data['relationships'] if i[0] == relationship_class_name]:
        to_arr.append((unit[1][0], unit[1][1]))


class ImportObject:
    def __init__(self, import_obj):
        self.name = import_obj[1]
        self.parameters = {}

    def add_parameter_value(self, import_obj):
        self.parameters[import_obj[2]] = import_obj[3]


class Repository:
    def __init__(self, db_data):
        self.energyProducers = {}
        self.powerPlants = {}
        self.substances = {}
        self.powerPlantsFuelMix = []
        self.tempFixedFuelPrices = {'biomass': 10, 'fuelOil': 20, 'hardCoal': 30, 'ligniteCoal': 10, 'naturalGas': 5,
                                    'uranium': 40}
        self.electricitySpotMarkets = {}
        self.powerPlantDispatchPlans = []

        db_objects_to_dict(db_data, self.energyProducers, 'EnergyProducers', EnergyProducer)
        db_objects_to_dict(db_data, self.powerPlants, 'PowerPlants', PowerPlant)
        db_objects_to_dict(db_data, self.substances, 'Substances', Substance)
        db_relationships_to_arr(db_data, self.powerPlantsFuelMix, 'PowerGeneratingTechnologyFuel')
        db_objects_to_dict(db_data, self.electricitySpotMarkets, 'ElectricitySpotMarkets', ElectricitySpotMarket)

    def get_powerplants_by_owner(self, owner):
        return [i for i in self.powerPlants.values() if i.parameters['Owner'] == owner]

    def get_substances_by_powerplant(self, powerplant_name):
        return [self.substances[i[1]] for i in self.powerPlantsFuelMix if i[0] == powerplant_name]

    def create_powerplant_dispatch_plan(self, plant, bidder, bidding_market, amount, price):
        ppdp = PowerPlantDispatchPlan()
        ppdp.plant = plant
        ppdp.bidder = bidder
        ppdp.biddingMarket = bidding_market
        ppdp.amount = amount
        ppdp.price = price
        self.powerPlantDispatchPlans.append(ppdp)


class EnergyProducer(ImportObject):
    pass


class PowerPlant(ImportObject):
    pass


class Substance(ImportObject):
    pass


class ElectricitySpotMarket(ImportObject):
    pass


class PowerPlantDispatchPlan:
    def __init__(self):
        self.plant = None
        self.bidder = None
        self.biddingMarket = None
        self.amount = None
        self.price = None
