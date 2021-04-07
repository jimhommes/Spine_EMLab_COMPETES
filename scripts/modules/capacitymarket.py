#
# The file responsible for all capacity market operations.
#
# Jim Hommes - 25-3-2021
#
import json
from modules.defaultmodule import DefaultModule


def calculate_marginal_fuel_cost(reps, plant):
    fc = 0
    for substance_in_fuel_mix in reps.get_substances_in_fuel_mix_by_plant(plant.name):
        amount = substance_in_fuel_mix.share
        fuel_price = reps.find_last_known_price_for_substance(substance_in_fuel_mix.substance.name, reps.current_tick)
        fc += amount * fuel_price
    return fc


def calculate_co2_tax_marginal_cost(reps, plant):
    co2_intensity = plant.calculate_emission_intensity(reps)
    print('TODO: Implement government CO2 tax')
#     co2_tax = government.get_co2_tax(tick)
    co2_tax = 1
    return co2_intensity * co2_tax


def calculate_marginal_cost_excl_co2_market_cost(reps, plant):
    mc = 0
    mc += calculate_marginal_fuel_cost(reps, plant)
    mc += calculate_co2_tax_marginal_cost(reps, plant)
    return mc


# Submit bids to the market
class CapacityMarketSubmitBids(DefaultModule):

    def __init__(self, reps):
        super().__init__('EM-Lab Capacity Market: Submit Bids', reps)

    def act(self):
        # For every energy producer we will submit bids to the Capacity Market
        for energy_producer in self.reps.energy_producers.values():

            # For every plant owned by energyProducer
            for powerplant in self.reps.get_power_plants_by_owner(energy_producer.name):
                market = self.reps.get_capacity_market_for_plant(powerplant.name)
                mc = calculate_marginal_cost_excl_co2_market_cost(self.reps, powerplant)
                capacity = self.reps.get_available_power_plant_capacity(powerplant.name)
                if capacity == 0:
                    price_to_bid = 0
                else:
                    price_to_bid = mc
                self.reps.create_power_plant_dispatch_plan(powerplant, energy_producer, market, capacity,
                                                           price_to_bid)


# Clear the market
class CapacityMarketClearing(DefaultModule):

    def __init__(self, reps):
        super().__init__('EM-Lab Capacity Market: Clear Market', reps)

    def act(self):
        peak_load = max(json.loads(self.reps.load['NL'].parameters['ldc'].to_database())['data'].values())
        for market in self.reps.capacity_markets.values():
            sdc = market.get_sloping_demand_curve(peak_load)
            sorted_ppdp = self.reps.get_sorted_dispatch_plans_by_market(market.name)
            clearing_price = 0
            total_supply = 0
            for ppdp in sorted_ppdp:
                if total_supply + ppdp.amount <= peak_load:
                    total_supply += ppdp.amount
                    clearing_price = sdc.get_price_at_volume(total_supply)
                    self.reps.set_power_plant_dispatch_plan_production(
                        ppdp, self.reps.power_plant_dispatch_plan_status_accepted, ppdp.amount)
                elif total_supply < peak_load:
                    clearing_price = sdc.get_price_at_volume(total_supply)
                    self.reps.set_power_plant_dispatch_plan_production(
                        ppdp, self.reps.power_plant_dispatch_plan_status_partly_accepted, peak_load - total_supply)
                    total_supply = peak_load
                else:
                    self.reps.set_power_plant_dispatch_plan_production(
                        ppdp, self.reps.power_plant_dispatch_plan_status_failed, 0)

            self.reps.create_market_clearing_point(market.name, clearing_price, total_supply)
