#
# All operations for the Electricity Spot Market
# Based on the role ClearIterativeCO2AndElectricitySpotMarketTwoCountryRole
#
# Jim Hommes - 25-3-2021
#
import json


# Submit bids
class ElectricitySpotMarketSubmitBids:

    def __init__(self, reps):
        self.reps = reps
        reps.dbrw.init_powerplantdispatchplan_structure()

    def act(self):
        # For every energy producer we will submit bids to the Capacity Market
        for energy_producer in self.reps.energy_producers.values():
            market = self.reps.electricity_spot_markets[energy_producer.parameters['investorMarket']]

            # For every plant owned by energyProducer
            for powerplant in self.reps.get_powerplants_by_owner(energy_producer.name):
                # Calculate marginal cost mc
                #   fuelConsumptionPerMWhElectricityProduced = 3600 / (pp.efficiency * ss.energydensity)
                #   lastKnownFuelPrice
                substances = self.reps.get_substances_by_powerplant(powerplant.name)
                if len(substances) > 0:  # Only done for 1 substance atm
                    mc = 3600 / (float(powerplant.parameters['Efficiency']) * float(
                        substances[0].parameters['energyDensity']))
                    capacity = int(powerplant.parameters['Capacity'])
                    self.reps.create_powerplant_dispatch_plan(powerplant, energy_producer, market, capacity, mc)


# Clear the market
class ElectricitySpotMarketClearing:

    def __init__(self, reps):
        self.reps = reps
        reps.dbrw.init_marketclearingpoint_structure()

    def act(self):
        # Calculate and submit Market Clearing Price
        peak_load = max(json.loads(self.reps.load['NL'].parameters['ldc'].to_database())['data'].values())
        for market in self.reps.electricity_spot_markets.values():
            sorted_ppdp = self.reps.get_sorted_dispatch_plans_by_market(market.name)
            clearing_price = 0
            total_load = 0
            for ppdp in sorted_ppdp:
                if total_load + ppdp.amount <= peak_load:
                    total_load += ppdp.amount
                    clearing_price = ppdp.price
                    self.reps.set_powerplant_dispatch_plan_production(
                        ppdp, self.reps.powerplant_dispatch_plan_status_accepted, ppdp.amount)
                elif total_load < peak_load:
                    clearing_price = ppdp.price
                    self.reps.set_powerplant_dispatch_plan_production(
                        ppdp, self.reps.powerplant_dispatch_plan_status_partly_accepted, peak_load - total_load)
                    total_load = peak_load
                else:
                    self.reps.set_powerplant_dispatch_plan_production(
                        ppdp, self.reps.powerplant_dispatch_plan_status_failed, 0)

            self.reps.create_market_clearingpoint(market.name, clearing_price, total_load)
