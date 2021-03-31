#
# The file responsible for all capacity market operations.
#
# Jim Hommes - 25-3-2021
#
import json
from modules.defaultmodule import DefaultModule


# Submit bids to the market
class CapacityMarketSubmitBids(DefaultModule):

    def __init__(self, reps):
        super().__init__('EM-Lab Capacity Market: Submit Bids', reps)

    def act(self):
        # For every energy producer we will submit bids to the Capacity Market
        for energy_producer in self.reps.energy_producers.values():
            market = self.reps.capacity_markets[energy_producer.parameters['capacityMarket']]

            # For every plant owned by energyProducer
            for powerplant in self.reps.get_power_plants_by_owner(energy_producer.name):
                # Calculate marginal cost mc
                #   fuelConsumptionPerMWhElectricityProduced = 3600 / (pp.efficiency * ss.energydensity)
                #   lastKnownFuelPrice
                substances = self.reps.get_substances_by_power_plant(powerplant.name)
                if len(substances) > 0:  # Only done for 1 substance atm
                    mc = 3600 / (float(powerplant.parameters['Efficiency']) * float(
                        substances[0].parameters['energyDensity']))
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
