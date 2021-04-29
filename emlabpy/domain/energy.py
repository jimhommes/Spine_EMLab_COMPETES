from domain.import_object import *


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

    def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
        if parameter_name == 'Technology':
            self.technology = reps.power_generating_technologies[parameter_value]
        elif parameter_name == 'Location':
            self.location = reps.power_grid_nodes[parameter_value]
        elif parameter_name == 'Age':
            self.age = int(parameter_value)
            self.construction_start_time = -1 * int(parameter_value)
        elif parameter_name == 'Owner':
            self.owner = reps.energy_producers[parameter_value]
        elif parameter_name == 'Capacity':
            self.capacity = int(parameter_value)
        elif parameter_name == 'Efficiency':
            self.efficiency = float(parameter_value)

    def calculate_emission_intensity(self, reps):
        emission = 0
        for substance_in_fuel_mix in reps.get_substances_in_fuel_mix_by_plant(self):
            amount_per_mw = substance_in_fuel_mix.share / (self.efficiency *
                                                           substance_in_fuel_mix.substance.energy_density)
            co2_density = substance_in_fuel_mix.substance.co2_density * (1 - float(
                self.technology.co2_capture_efficiency))
            emission_for_this_fuel = amount_per_mw * co2_density
            emission += emission_for_this_fuel
        return emission

    def get_actual_fixed_operating_cost(self):
        return self.technology.get_fixed_operating_cost(self.construction_start_time +
                                                        int(self.technology.expected_leadtime) +
                                                        int(self.technology.expected_permittime)) \
               * self.get_actual_nominal_capacity()

    def get_actual_nominal_capacity(self):
        if self.capacity == 0:
            return self.technology.capacity * float(self.location.parameters['CapacityMultiplicationFactor'])
        else:
            return self.capacity

    def calculate_marginal_fuel_cost_by_tick(self, reps, time):
        fc = 0
        for substance_in_fuel_mix in reps.get_substances_in_fuel_mix_by_plant(self):
            amount_per_mw = substance_in_fuel_mix.share / (self.efficiency *
                                                           substance_in_fuel_mix.substance.energy_density)
            fuel_price = substance_in_fuel_mix.substance.get_price_for_tick(time)
            fc += amount_per_mw * fuel_price
        return fc

    def calculate_co2_tax_marginal_cost(self, reps):
        co2_intensity = self.calculate_emission_intensity(reps)
        co2_tax = 0
        return co2_intensity * co2_tax

    def calculate_marginal_cost_excl_co2_market_cost(self, reps, time):
        mc = 0
        mc += self.calculate_marginal_fuel_cost_by_tick(reps, time)
        mc += self.calculate_co2_tax_marginal_cost(reps)
        return mc

    def get_load_factor_for_production(self, production):
        if self.capacity != 0:
            return production / self.capacity
        else:
            return 0


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

    def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
        if parameter_name == 'capacity':
            self.capacity = int(parameter_value)
        elif parameter_name == 'intermittent':
            self.intermittent = 'TRUE' == parameter_value
        elif parameter_name == 'applicableForLongTermContract':
            self.applicable_for_long_term_contract = bool(parameter_value)
        elif parameter_name == 'peakSegmentDependentAvailability':
            self.peak_segment_dependent_availability = float(parameter_value)
        elif parameter_name == 'baseSegmentDependentAvailability':
            self.base_segment_dependent_availability = float(parameter_value)
        elif parameter_name == 'maximumInstalledCapacityFractionPerAgent':
            self.maximum_installed_capacity_fraction_per_agent = float(parameter_value)
        elif parameter_name == 'maximumInstalledCapacityFractionInCountry':
            self.maximum_installed_capacity_fraction_in_country = float(parameter_value)
        elif parameter_name == 'minimumFuelQuality':
            self.minimum_fuel_quality = float(parameter_value)
        elif parameter_name == 'expectedPermittime':
            self.expected_permittime = int(parameter_value)
        elif parameter_name == 'expectedLeadtime':
            self.expected_leadtime = int(parameter_value)
        elif parameter_name == 'expectedLifetime':
            self.expected_lifetime = int(parameter_value)
        elif parameter_name == 'fixedOperatingCostModifierAfterLifetime':
            self.fixed_operating_cost_modifier_after_lifetime = float(parameter_value)
        elif parameter_name == 'minimumRunningHours':
            self.minimum_running_hours = int(parameter_value)
        elif parameter_name == 'depreciationTime':
            self.depreciation_time = int(parameter_value)
        elif parameter_name == 'efficiencyTimeSeries':
            self.efficiency_time_series = reps.trends[parameter_value]
        elif parameter_name == 'fixedOperatingCostTimeSeries':
            self.fixed_operating_cost_time_series = reps.trends[parameter_value]
        elif parameter_name == 'investmentCostTimeSeries':
            self.investment_cost_time_series = reps.trends[parameter_value]
        elif parameter_name == 'co2CaptureEfficiency':
            self.co2_capture_efficiency = float(parameter_value)

    def get_fixed_operating_cost(self, time):
        return self.fixed_operating_cost_time_series.get_value(time)


class Substance(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        self.co2_density = 0
        self.energy_density = 0
        self.quality = 0
        self.trend = None

    def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
        if parameter_name == 'co2Density':
            self.co2_density = float(parameter_value)
        elif parameter_name == 'energyDensity':
            self.energy_density = float(parameter_value)
        elif parameter_name == 'quality':
            self.quality = float(parameter_value)
        elif parameter_name == 'trend':
            self.trend = reps.trends[parameter_value]

    def get_price_for_tick(self, tick):
        return self.trend.get_value(tick)


class SubstanceInFuelMix:
    def __init__(self, substance, share):
        self.substance = substance
        self.share = share


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

    def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
        self.tick = int(alternative)
        if parameter_name == 'Plant':
            self.plant = reps.power_plants[parameter_value]
        elif parameter_name == 'EnergyProducer':
            self.bidder = reps.energy_producers[parameter_value]
        if parameter_name == 'Market':
            self.bidding_market = reps.capacity_markets[parameter_value] if \
                parameter_value in reps.capacity_markets.keys() \
                else reps.electricity_spot_markets[parameter_value]
        if parameter_name == 'Capacity':
            self.amount = parameter_value
        if parameter_name == 'AcceptedAmount':
            self.accepted_amount = float(parameter_value)
        if parameter_name == 'Price':
            self.price = float(parameter_value)
        if parameter_name == 'Status':
            self.status = parameter_value
