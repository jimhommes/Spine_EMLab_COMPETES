"""
The file responsible for all capacity market operations.

Jim Hommes - 25-3-2021
"""
import json
from modules.market import Market


class CapacityMarketSubmitBids(Market):
    """The class that submits all bids to the Capacity Market"""

    def __init__(self, reps):
        super().__init__('EM-Lab Capacity Market: Submit Bids', reps)

    def act(self):
        # For every energy producer we will submit bids to the Capacity Market
        for energy_producer in self.reps.energy_producers.values():

            # For every plant owned by energyProducer
            for powerplant in self.reps.get_power_plants_by_owner(energy_producer):
                market = self.reps.get_capacity_market_for_plant(powerplant)
                emarket = self.reps.get_electricity_spot_market_for_plant(powerplant)
                mc = self.calculate_marginal_cost_excl_co2_market_cost(powerplant)
                fixed_on_m_cost = powerplant.get_actual_fixed_operating_cost()

                clearing_point_price = self.reps.get_market_clearing_point_price_for_market_and_time(
                    self.reps.current_tick - 1, emarket)

                powerplant_load_factor = 1
                print('TODO: Plant load factor, necessary?? Upscales with segment part...')

                expected_electricity_revenues = 0
                if clearing_point_price >= mc:
                    expected_electricity_revenues += (clearing_point_price - mc) * \
                                                     powerplant.get_actual_nominal_capacity() * \
                                                     powerplant_load_factor * 8760

                capacity = self.reps.get_available_power_plant_capacity(powerplant.name)
                print('TODO: Discuss - in emlab full capacity is bid')

                net_revenues = expected_electricity_revenues - fixed_on_m_cost
                price_to_bid = 0
                if self.reps.current_tick > 0:
                    if net_revenues <= 0:
                        price_to_bid = -1 * net_revenues / (powerplant.get_actual_nominal_capacity() *
                                                            powerplant.technology.peak_segment_dependent_availability)

                self.reps.create_power_plant_dispatch_plan(powerplant, energy_producer, market, capacity,
                                                           price_to_bid)


class CapacityMarketClearing(Market):
    """The class that clears the Capacity Market based on the Sloping Demand curve"""

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
