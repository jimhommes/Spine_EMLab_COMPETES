"""
The Repository: home of all objects that play a part in the model.
All objects are read through the SpineDBReader and stored in the Repository.

Jim Hommes - 25-3-2021
"""
from datetime import datetime


class ImportObject:
    """
    Parent Class for all objects imported from Spine
    Will probably become redundant in the future as it's neater to translate parameters to Python parameters
    instead of a dict like this
    """

    def __init__(self, name):
        self.name = name
        self.parameters = {}

    def add_parameter_value(self, reps, import_obj):
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
        self.power_plant_dispatch_plans = {}
        self.power_generating_technologies = {}
        self.load = {}
        self.market_clearing_points = {}
        self.power_grid_nodes = {}
        self.geometric_trends = {}

        self.temporary_fixed_fuel_prices = {'biomass': 10, 'fuelOil': 20, 'hardCoal': 30, 'ligniteCoal': 10,
                                            'naturalGas': 5,
                                            'uranium': 40}

        self.power_plant_dispatch_plan_status_accepted = 'Accepted'
        self.power_plant_dispatch_plan_status_failed = 'Failed'
        self.power_plant_dispatch_plan_status_partly_accepted = 'Partly Accepted'
        self.power_plant_dispatch_plan_status_awaiting = 'Awaiting'

    def get_power_plants_by_owner(self, owner):
        return [i for i in self.power_plants.values() if i.owner == owner]

    def create_power_plant_dispatch_plan(self, plant, bidder, bidding_market, amount, price):
        name = 'PowerPlantDispatchPlan ' + str(datetime.now())
        ppdp = PowerPlantDispatchPlan(name)
        ppdp.plant = plant
        ppdp.bidder = bidder
        ppdp.bidding_market = bidding_market
        ppdp.amount = amount
        ppdp.price = price
        ppdp.status = self.power_plant_dispatch_plan_status_awaiting
        ppdp.accepted_amount = 0
        self.power_plant_dispatch_plans[name] = ppdp
        self.dbrw.stage_power_plant_dispatch_plan(ppdp, self.current_tick)

    def get_sorted_dispatch_plans_by_market(self, market_name):
        return sorted([i for i in self.power_plant_dispatch_plans.values() if i.bidding_market.name == market_name],
                      key=lambda i: i.price)

    def create_market_clearing_point(self, market, price, capacity):
        name = 'MarketClearingPoint ' + str(datetime.now())
        mcp = MarketClearingPoint(name)
        mcp.market = market
        mcp.price = price
        mcp.capacity = capacity
        self.market_clearing_points[name] = mcp
        self.dbrw.stage_market_clearing_point(mcp, self.current_tick)

    def get_available_power_plant_capacity(self, plant_name):
        plant = self.power_plants[plant_name]
        ppdps_sum_accepted_amount = sum([float(i.accepted_amount) for i in
                                         self.get_power_plant_dispatch_plans_by_plant(plant_name)])
        return plant.capacity - ppdps_sum_accepted_amount

    def get_power_plant_dispatch_plans_by_plant(self, plant_name):
        return [i for i in self.power_plant_dispatch_plans.values() if i.plant.name == plant_name]

    def set_power_plant_dispatch_plan_production(self, ppdp, status, accepted_amount):
        ppdp.status = status
        ppdp.accepted_amount = accepted_amount

        self.dbrw.stage_power_plant_dispatch_plan(ppdp, self.current_tick)

    def get_electricity_spot_market_for_plant(self, plant):
        zone = plant.location.parameters['Zone']
        res = [i for i in self.electricity_spot_markets.values() if i.parameters['zone'] == zone]
        if len(res) == 0:
            return None
        else:
            return res[0]

    def get_capacity_market_for_plant(self, plant):
        zone = plant.location.parameters['Zone']
        res = [i for i in self.capacity_markets.values() if i.parameters['zone'] == zone]
        if len(res) == 0:
            return None
        else:
            return res[0]

    def get_substances_in_fuel_mix_by_plant(self, plant):
        if plant.technology.name in self.power_plants_fuel_mix.keys():
            return self.power_plants_fuel_mix[plant.technology.name]
        else:
            return []

    def find_last_known_price_for_substance(self, substance_name, tick):
        print('TODO: Finding last known price for substance - taking fixed price now')
        return self.temporary_fixed_fuel_prices[substance_name]

    def get_market_clearing_point_for_market_and_time(self, tick, market):
        res = [i for i in self.market_clearing_points.values() if i.market == market and i.tick == tick]
        if len(res) > 0:
            return res[0]
        else:
            return None

    def get_market_clearing_point_price_for_market_and_time(self, tick, market):
        if tick >= 0:
            mcp = self.get_market_clearing_point_for_market_and_time(tick, market)
            return mcp.price
        else:
            return 0


"""
From here on defitions of Objects that are imported. Pass because they inherit name and parameters from ImportObject
"""


class EnergyProducer(ImportObject):
    pass


class PowerPlant(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        self.technology = None
        self.location = None
        self.age = 0
        self.owner = None
        self.capacity = 0
        self.efficiency = 0
        self.construction_start_time = 0

    def add_parameter_value(self, reps, import_obj):
        if import_obj[2] == 'Technology':
            self.technology = reps.power_generating_technologies[import_obj[3]]
        elif import_obj[2] == 'Location':
            self.location = reps.power_grid_nodes[import_obj[3]]
        elif import_obj[2] == 'Age':
            self.age = int(import_obj[3])
            self.construction_start_time = -1 * int(import_obj[3])
        elif import_obj[2] == 'Owner':
            self.owner = reps.energy_producers[import_obj[3]]
        elif import_obj[2] == 'Capacity':
            self.capacity = int(import_obj[3])
        elif import_obj[2] == 'Efficiency':
            self.efficiency = float(import_obj[3])

    def calculate_emission_intensity(self, reps):
        emission = 0
        for substance_in_fuel_mix in reps.get_substances_in_fuel_mix_by_plant(self):
            fuel_amount = substance_in_fuel_mix.share
            co2_density = float(substance_in_fuel_mix.substance.parameters['co2Density']) * (1 - float(
                self.technology.co2_capture_efficiency))
            emission_for_this_fuel = fuel_amount * co2_density
            emission += emission_for_this_fuel
        return emission

    def get_actual_fixed_operating_cost(self):
        return self.technology.get_fixed_operating_cost(self.construction_start_time +
                                                        int(self.technology.expected_leadtime) +
                                                        int(self.technology.expected_permittime)) \
               * self.get_actual_nominal_capacity()

    def get_actual_nominal_capacity(self):
        return self.technology.capacity * float(self.location.parameters['CapacityMultiplicationFactor'])


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
    def __init__(self, name):
        super().__init__(name)
        self.capacity = 0
        self.intermittent = False
        self.applicable_for_long_term_contract = False
        self.peak_segment_dependent_availability = 0
        self.base_segment_dependent_availability = 0
        self.maximum_installed_capacity_fraction_per_agent = 0
        self.maximum_installed_capacity_fraction_in_country = 0
        self.minimum_fuel_quality = 0
        self.expected_permittime = 0
        self.expected_leadtime = 0
        self.expected_lifetime = 0
        self.fixed_operating_cost_modifier_after_lifetime = 0
        self.minimum_running_hours = 0
        self.depreciation_time = 0
        self.efficiency_time_series = None
        self.fixed_operating_cost_time_series = None
        self.investment_cost_time_series = None
        self.co2_capture_efficiency = 0

    def add_parameter_value(self, reps, import_obj):
        if import_obj[2] == 'capacity':
            self.capacity = int(import_obj[3])
        elif import_obj[2] == 'intermittent':
            self.intermittent = 'TRUE' == import_obj[3]
        elif import_obj[2] == 'applicableForLongTermContract':
            self.applicable_for_long_term_contract = 'TRUE' == import_obj[3]
        elif import_obj[2] == 'peakSegmentDependentAvailability':
            self.peak_segment_dependent_availability = float(import_obj[3])
        elif import_obj[2] == 'baseSegmentDependentAvailability':
            self.base_segment_dependent_availability = float(import_obj[3])
        elif import_obj[2] == 'maximumInstalledCapacityFractionPerAgent':
            self.maximum_installed_capacity_fraction_per_agent = float(import_obj[3])
        elif import_obj[2] == 'maximumInstalledCapacityFractionInCountry':
            self.maximum_installed_capacity_fraction_in_country = float(import_obj[3])
        elif import_obj[2] == 'minimumFuelQuality':
            self.minimum_fuel_quality = float(import_obj[3])
        elif import_obj[2] == 'expectedPermittime':
            self.expected_permittime = int(import_obj[3])
        elif import_obj[2] == 'expectedLeadtime':
            self.expected_leadtime = int(import_obj[3])
        elif import_obj[2] == 'expectedLifetime':
            self.expected_lifetime = int(import_obj[3])
        elif import_obj[2] == 'fixedOperatingCostModifierAfterLifetime':
            self.fixed_operating_cost_modifier_after_lifetime = float(import_obj[3])
        elif import_obj[2] == 'minimumRunningHours':
            self.minimum_running_hours = int(import_obj[3])
        elif import_obj[2] == 'depreciationTime':
            self.depreciation_time = int(import_obj[3])
        elif import_obj[2] == 'efficiencyTimeSeries':
            self.efficiency_time_series = reps.geometric_trends[import_obj[3]]
        elif import_obj[2] == 'fixedOperatingCostTimeSeries':
            self.fixed_operating_cost_time_series = reps.geometric_trends[import_obj[3]]
        elif import_obj[2] == 'investmentCostTimeSeries':
            self.investment_cost_time_series = reps.geometric_trends[import_obj[3]]
        elif import_obj[2] == 'co2CaptureEfficiency':
            self.co2_capture_efficiency = float(import_obj[3])

    def get_fixed_operating_cost(self, time):
        return self.fixed_operating_cost_time_series.get_value(time)


class HourlyLoad(ImportObject):
    pass


class PowerGridNode(ImportObject):
    pass


class PowerPlantDispatchPlan(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        self.plant = None
        self.bidder = None
        self.bidding_market = None
        self.amount = None
        self.price = None
        self.status = 'Awaiting confirmation'
        self.accepted_amount = 0
        self.tick = -1

    def add_parameter_value(self, reps, import_obj):
        self.tick = int(import_obj[4])
        if import_obj[2] == 'Plant':
            self.plant = reps.power_plants[import_obj[3]]
        elif import_obj[2] == 'EnergyProducer':
            self.bidder = reps.energy_producers[import_obj[3]]
        if import_obj[2] == 'Market':
            self.bidding_market = reps.capacity_markets[import_obj[3]] if \
                import_obj[3] in reps.capacity_markets.keys() \
                else reps.electricity_spot_markets[import_obj[3]]
        if import_obj[2] == 'Capacity':
            self.amount = import_obj[3]
        if import_obj[2] == 'AcceptedAmount':
            self.accepted_amount = float(import_obj[3])
        if import_obj[2] == 'Price':
            self.price = float(import_obj[3])
        if import_obj[2] == 'Status':
            self.status = import_obj[3]


class MarketClearingPoint(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        self.market = None
        self.price = 0
        self.capacity = 0
        self.tick = -1

    def add_parameter_value(self, reps, import_obj):
        self.tick = int(import_obj[4])
        if import_obj[2] == 'Price':
            self.price = float(import_obj[3])
        if import_obj[2] == 'Market':
            if import_obj[3] in reps.capacity_markets.keys():
                self.market = reps.capacity_markets[import_obj[3]]
            else:
                self.market = reps.electricity_spot_markets[import_obj[3]]
        if import_obj[2] == 'TotalCapacity':
            self.capacity = float(import_obj[3])


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


class GeometricTrend(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        self.start = 0
        self.growth_rate = 0

    def add_parameter_value(self, reps, import_obj):
        if import_obj[2] == 'start':
            self.start = int(import_obj[3])
        elif import_obj[2] == 'growthRate':
            self.growth_rate = float(import_obj[3])

    def get_value(self, time):
        return pow(1 + self.growth_rate, time) * self.start
