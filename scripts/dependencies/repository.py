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
        if import_obj[4] == 'init':
            self.parameters[import_obj[2]] = import_obj[3]
        else:
            self.add_parameter_value_for_tick(import_obj)

    def add_parameter_value_for_tick(self, import_obj):
        pass


# The Repository class reads DB data at initialization and loads all objects and relationships
# Also provides all functions that require e.g. sorting
class Repository:
    def __init__(self):
        self.dbrw = None

        self.current_tick = 0

        self.energy_producers = {}
        self.power_plants = {}
        self.substances = {}
        self.power_plants_fuel_mix = []
        self.electricity_spot_markets = {}
        self.capacity_markets = {}
        self.power_plant_dispatch_plans = []
        self.power_generating_technologies = {}
        self.load = {}
        self.market_clearing_points = []

        self.temporary_fixed_fuel_prices = {'biomass': 10, 'fuelOil': 20, 'hardCoal': 30, 'ligniteCoal': 10,
                                            'naturalGas': 5,
                                            'uranium': 40}

        self.power_plant_dispatch_plan_status_accepted = 'Accepted'
        self.power_plant_dispatch_plan_status_failed = 'Failed'
        self.power_plant_dispatch_plan_status_partly_accepted = 'Partly Accepted'
        self.power_plant_dispatch_plan_status_awaiting = 'Awaiting'

    def get_power_plants_by_owner(self, owner):
        return [i for i in self.power_plants.values() if i.parameters['Owner'] == owner]

    def get_substances_by_power_plant(self, powerplant_name):
        return [self.substances[i[1]] for i in self.power_plants_fuel_mix
                if i[0] == self.power_plants[powerplant_name].parameters['Technology']]

    def create_power_plant_dispatch_plan(self, plant, bidder, bidding_market, amount, price):
        ppdp = PowerPlantDispatchPlan()
        ppdp.plant = plant
        ppdp.bidder = bidder
        ppdp.bidding_market = bidding_market
        ppdp.amount = amount
        ppdp.price = price
        ppdp.status = self.power_plant_dispatch_plan_status_awaiting
        ppdp.accepted_amount = 0
        self.power_plant_dispatch_plans.append(ppdp)
        self.dbrw.stage_power_plant_dispatch_plan(ppdp, self.current_tick)

    def get_sorted_dispatch_plans_by_market(self, market_name):
        return sorted([i for i in self.power_plant_dispatch_plans if i.bidding_market.name == market_name],
                      key=lambda i: i.price)

    def create_market_clearing_point(self, market, price, capacity):
        mcp = MarketClearingPoint(market, price, capacity)
        self.market_clearing_points.append(mcp)
        self.dbrw.stage_market_clearing_point(mcp, self.current_tick)

    def get_available_power_plant_capacity(self, plant_name):
        plant = self.power_plants[plant_name]
        ppdps_sum_accepted_amount = sum([float(i.accepted_amount) for i in
                                         self.get_power_plant_dispatch_plans_by_plant(plant_name)])
        return float(plant.parameters['Capacity']) - ppdps_sum_accepted_amount

    def get_power_plant_dispatch_plans_by_plant(self, plant_name):
        return [i for i in self.power_plant_dispatch_plans if i.plant.name == plant_name]

    def set_power_plant_dispatch_plan_production(self, ppdp, status, accepted_amount):
        ppdp.status = status
        ppdp.accepted_amount = accepted_amount

        self.dbrw.stage_power_plant_dispatch_plan(ppdp, self.current_tick)


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
        return SlopingDemandCurve(float(self.parameters['InstalledReserveMargin']),
                                  float(self.parameters['LowerMargin']),
                                  float(self.parameters['UpperMargin']), d_peak, float(self.parameters['PriceCap']))


class PowerGeneratingTechnology(ImportObject):
    pass


class HourlyLoad(ImportObject):
    pass


class PowerPlantDispatchPlan:
    def __init__(self):
        self.plant = None
        self.bidder = None
        self.bidding_market = None
        self.amount = None
        self.price = None
        self.status = 'Awaiting confirmation'
        self.accepted_amount = 0
        self.tick = -1


class MarketClearingPoint:
    def __init__(self):
        self.market = None
        self.price = 0
        self.capacity = 0
        self.tick = -1


class SlopingDemandCurve:
    def __init__(self, irm, lm, um, d_peak, price_cap):
        self.irm = irm
        self.lm = lm
        self.lm_volume = d_peak * (1 + irm - lm)
        self.um = um
        self.um_volume = d_peak * (1 + irm + um)
        self.d_peak = d_peak
        self.price_cap = price_cap

    def get_price_at_volume(self, volume):
        m = self.price_cap / (self.um_volume - self.lm_volume)
        if volume < self.lm_volume:
            return self.price_cap
        elif self.lm_volume <= volume <= self.um_volume:
            return self.price_cap - m * (volume - self.lm_volume)
        elif self.um_volume < volume:
            return 0
