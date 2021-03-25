#
# The Repository: home of all objects that play a part in the model.
# All objects are read through the SpineDBReader and stored in the Repository.
#
# Jim Hommes - 25-3-2021
#
from datetime import datetime


# Parent Class for all objects imported from Spine
# Will probably become redundant in the future as it's neater to translate parameters to Python parameters
#   instead of a dict like this
class ImportObject:
    def __init__(self, import_obj):
        self.name = import_obj[1]
        self.parameters = {}

    def add_parameter_value(self, import_obj):
        self.parameters[import_obj[2]] = import_obj[3]


# The Repository class reads DB data at initialization and loads all objects and relationships
# Also provides all functions that require e.g. sorting
class Repository:
    def __init__(self):
        self.dbrw = None

        self.energyProducers = {}
        self.powerPlants = {}
        self.substances = {}
        self.powerPlantsFuelMix = []
        self.electricitySpotMarkets = {}
        self.powerPlantDispatchPlans = []
        self.powerGeneratingTechnologies = {}
        self.load = {}
        self.marketClearingPoints = []

        self.tempFixedFuelPrices = {'biomass': 10, 'fuelOil': 20, 'hardCoal': 30, 'ligniteCoal': 10, 'naturalGas': 5,
                                    'uranium': 40}

    def get_powerplants_by_owner(self, owner):
        return [i for i in self.powerPlants.values() if i.parameters['Owner'] == owner]

    def get_substances_by_powerplant(self, powerplant_name):
        return [self.substances[i[1]] for i in self.powerPlantsFuelMix if i[0] == self.powerPlants[powerplant_name]
            .parameters['Technology']]

    def create_powerplant_dispatch_plan(self, plant, bidder, bidding_market, amount, price):
        ppdp = PowerPlantDispatchPlan()
        ppdp.plant = plant
        ppdp.bidder = bidder
        ppdp.biddingMarket = bidding_market
        ppdp.amount = amount
        ppdp.price = price
        self.powerPlantDispatchPlans.append(ppdp)

        self.dbrw.import_object(self.dbrw.ppdp_object_class_name, plant)
        self.dbrw.import_object_parameter_values(self.dbrw.ppdp_object_class_name, plant,
                                               [('Market', bidding_market), ('Price', price),
                                                ('Capacity', amount),
                                                ('EnergyProducer', bidder)])
        self.dbrw.commit('EM-Lab Capacity Market: Submit Bids: ' + str(datetime.now()))

    def get_sorted_dispatch_plans_by_market(self, market_name):
        return sorted([i for i in self.powerPlantDispatchPlans if i.biddingMarket.name == market_name],
                      key=lambda i: i.price)

    def create_market_clearingpoint(self, market_name, clearing_price, total_capacity):
        mcp = MarketClearingPoint(market_name, clearing_price, total_capacity)
        self.marketClearingPoints.append(mcp)

        self.dbrw.import_object(self.dbrw.mcp_object_class_name, 'ClearingPoint')
        self.dbrw.import_object_parameter_values(self.dbrw.mcp_object_class_name, 'ClearingPoint',
                                                 [('Market', market_name), ('Price', clearing_price),
                                                  ('TotalCapacity', total_capacity)])
        self.dbrw.commit('EM-Lab Capacity Market: Submit Clearing Point: ' + str(datetime.now()))


# Objects that are imported. Pass because they inherit name and parameters from ImportObject

class EnergyProducer(ImportObject):
    pass


class PowerPlant(ImportObject):
    pass


class Substance(ImportObject):
    pass


class ElectricitySpotMarket(ImportObject):
    pass


class PowerGeneratingTechnology(ImportObject):
    pass


class HourlyLoad(ImportObject):
    pass


class PowerPlantDispatchPlan:
    def __init__(self):
        self.plant = None
        self.bidder = None
        self.biddingMarket = None
        self.amount = None
        self.price = None


class MarketClearingPoint:
    def __init__(self, market, price, capacity):
        self.market = market
        self.price = price
        self.capacity = capacity
