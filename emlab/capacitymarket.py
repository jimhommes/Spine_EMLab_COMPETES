#
# The file responsible for all capacity market operations.
#
# Jim Hommes - 25-3-2021
#
import json


# Submit bids to the market
class CapacityMarketSubmitBids:

    def __init__(self, reps):
        self.reps = reps

    def act(self):
        # For every energy producer we will submit bids to the Capacity Market
        for energyProducer in self.reps.energyProducers.values():
            market = self.reps.capacityMarkets[energyProducer.parameters['capacityMarket']]

            # For every plant owned by energyProducer
            for powerPlant in self.reps.get_powerplants_by_owner(energyProducer.name):
                # Calculate marginal cost mc
                #   fuelConsumptionPerMWhElectricityProduced = 3600 / (pp.efficiency * ss.energydensity)
                #   lastKnownFuelPrice
                substances = self.reps.get_substances_by_powerplant(powerPlant.name)
                if len(substances) > 0:  # Only done for 1 substance atm
                    mc = 3600 / (float(powerPlant.parameters['Efficiency']) * float(
                        substances[0].parameters['energyDensity']))
                    capacity = self.reps.get_available_powerplant_capacity(powerPlant.name)
                    if capacity == 0:
                        price_to_bid = 0
                    else:
                        price_to_bid = mc
                    self.reps.create_powerplant_dispatch_plan(powerPlant, energyProducer, market, capacity, price_to_bid)


# Clear the market
class CapacityMarketClearing:

    def __init__(self, reps):
        self.reps = reps

    def act(self):
        peak_load = max(json.loads(self.reps.load['NL'].parameters['ldc'].to_database())['data'].values())
        for market in self.reps.capacityMarkets.values():
            sdc = market.get_sloping_demand_curve(peak_load)
            sorted_ppdp = self.reps.get_sorted_dispatch_plans_by_market(market.name)
            clearing_price = 0
            total_supply = 0
            for ppdp in sorted_ppdp:
                total_supply += ppdp.amount
                clearing_price = sdc.get_price_at_volume(total_supply)
                if ppdp.price >= clearing_price:
                    break

            self.reps.create_market_clearingpoint(market.name, clearing_price, total_supply)
