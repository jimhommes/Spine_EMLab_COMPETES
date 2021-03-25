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
        self.capacityMarkets = {}
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

        self.dbrw.import_object(self.dbrw.ppdp_object_class_name, plant.name)
        self.dbrw.import_object_parameter_values(self.dbrw.ppdp_object_class_name, plant.name,
                                                 [('Market', bidding_market.name), ('Price', price),
                                                  ('Capacity', amount),
                                                  ('EnergyProducer', bidder.name)])
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

    def get_available_powerplant_capacity(self, plant_name):
        substances = self.get_substances_by_powerplant(plant_name)
        if len(substances) > 0:  # Only done for 1 substance atm
            plant = self.powerPlants[plant_name]
            mc = 3600 / (float(plant.parameters['Efficiency']) * float(
                substances[0].parameters['energyDensity']))
            # Check if plant's bid is accepted
            mcp_price = self.marketClearingPoints[0]
            if mcp_price.price <= mc:
                return int(plant.parameters['Capacity'])
            else:
                return 0


# Objects that are imported. Pass because they inherit name and parameters from ImportObject

class EnergyProducer(ImportObject):
    pass


class PowerPlant(ImportObject):
    pass


class Substance(ImportObject):
    pass


class ElectricitySpotMarket(ImportObject):
    pass


class CapacityMarket(ImportObject):

    def get_sloping_demand_curve(self, d_peak):
        return SlopingDemandCurve(float(self.parameters['InstalledReserveMargin']), float(self.parameters['LowerMargin']),
                                  float(self.parameters['UpperMargin']), d_peak, float(self.parameters['PriceCap']))


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
        self.status = 'Awaiting confirmation'
        self.acceptedAmount = 0


class MarketClearingPoint:
    def __init__(self, market, price, capacity):
        self.market = market
        self.price = price
        self.capacity = capacity


class SlopingDemandCurve:
    def __init__(self, irm, lm, um, d_peak, price_cap):
        self.irm = irm
        self.lm = lm
        self.lmVolume = d_peak * (1 + irm - lm)
        self.um = um
        self.umVolume = d_peak * (1 + irm + um)
        self.d_peak = d_peak
        self.price_cap = price_cap

    def get_price_at_volume(self, volume):
        m = self.price_cap / (self.umVolume - self.lmVolume)
        if volume < self.lmVolume:
            return self.price_cap
        elif self.lmVolume <= volume <= self.umVolume:
            return self.price_cap - m * (volume - self.lmVolume)
        elif self.umVolume < volume:
            return 0
