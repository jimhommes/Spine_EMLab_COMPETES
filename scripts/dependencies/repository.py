"""
The Repository: home of all objects that play a part in the model.
All objects are read through the SpineDBReader and stored in the Repository.

Jim Hommes - 25-3-2021
"""


class ImportObject:
    """
    Parent Class for all objects imported from Spine
    Will probably become redundant in the future as it's neater to translate parameters to Python parameters
    instead of a dict like this
    """
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


class Repository:
    """
    The Repository class reads DB data at initialization and loads all objects and relationships
    Also provides all functions that require e.g. sorting
    """
    def __init__(self):
        self.dbrw = None

        self.current_tick = 0

        self.energy_producers = {}
        self.power_plants = {}
        self.substances = {}
        self.power_plants_fuel_mix = {}
        self.electricity_spot_markets = {}
        self.capacity_markets = {}
        self.power_plant_dispatch_plans = []
        self.power_generating_technologies = {}
        self.load = {}
        self.market_clearing_points = []
        self.power_grid_nodes = {}

        self.temporary_fixed_fuel_prices = {'biomass': 10, 'fuelOil': 20, 'hardCoal': 30, 'ligniteCoal': 10,
                                            'naturalGas': 5,
                                            'uranium': 40}

        self.power_plant_dispatch_plan_status_accepted = 'Accepted'
        self.power_plant_dispatch_plan_status_failed = 'Failed'
        self.power_plant_dispatch_plan_status_partly_accepted = 'Partly Accepted'
        self.power_plant_dispatch_plan_status_awaiting = 'Awaiting'

    def get_power_plants_by_owner(self, owner):
        return [i for i in self.power_plants.values() if i.parameters['Owner'] == owner]

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
        mcp = MarketClearingPoint()
        mcp.market = market
        mcp.price = price
        mcp.capacity = capacity
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

    def get_electricity_spot_market_for_plant(self, plant_name):
        plant = self.power_plants[plant_name]
        node = plant.parameters['Location']
        zone = self.power_grid_nodes[node].parameters['Zone']
        res = [i for i in self.electricity_spot_markets.values() if i.parameters['zone'] == zone]
        if len(res) == 0:
            return None
        else:
            return res[0]

    def get_capacity_market_for_plant(self, plant_name):
        plant = self.power_plants[plant_name]
        node = plant.parameters['Location']
        zone = self.power_grid_nodes[node].parameters['Zone']
        res = [i for i in self.capacity_markets.values() if i.parameters['zone'] == zone]
        if len(res) == 0:
            return None
        else:
            return res[0]

    def get_substances_in_fuel_mix_by_plant(self, plant_name):
        technology = self.power_plants[plant_name].parameters['Technology']
        if technology in self.power_plants_fuel_mix.keys():
            return self.power_plants_fuel_mix[self.power_plants[plant_name].parameters['Technology']]
        else:
            return []

    def find_last_known_price_for_substance(self, substance_name, tick):
        print('TODO: Finding last known price for substance - taking fixed price now')
        return self.temporary_fixed_fuel_prices[substance_name]


"""
From here on defitions of Objects that are imported. Pass because they inherit name and parameters from ImportObject
"""


class EnergyProducer(ImportObject):
    pass


class PowerPlant(ImportObject):
    def calculate_emission_intensity(self, reps):
        emission = 0
        for substance_in_fuel_mix in reps.get_substances_in_fuel_mix_by_plant(self.name):
            fuel_amount = substance_in_fuel_mix.share
            co2_density = float(substance_in_fuel_mix.substance.parameters['co2Density']) * (1 - float(
                reps.power_generating_technologies[self.parameters['Technology']].parameters['co2CaptureEfficiency']))
            emission_for_this_fuel = fuel_amount * co2_density
            emission += emission_for_this_fuel
        return emission


class Substance(ImportObject):
    pass


class SubstanceInFuelMix:
    def __init__(self, substance, share):
        self.substance = substance
        self.share = share


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


class PowerGridNode(ImportObject):
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
