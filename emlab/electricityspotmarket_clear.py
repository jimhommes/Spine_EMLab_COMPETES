#
# Clearing the Electricity Spot Market.
# Based on the role ClearIterativeCO2AndElectricitySpotMarketTwoCountryRole
#
# Jim Hommes - 25-3-2021
#
import json


class ElectricitySpotMarketClearing:

    def __init__(self, reps):
        self.reps = reps
        reps.dbrw.init_marketclearingpoint_structure()

    def act(self):
        # Calculate and submit Market Clearing Price
        peak_load = max(json.loads(self.reps.load['NL'].parameters['ldc'].to_database())['data'].values())
        for market in self.reps.electricitySpotMarkets.values():
            sorted_ppdp = self.reps.get_sorted_dispatch_plans_by_market(market.name)
            clearing_price = 0
            total_load = 0
            for ppdp in sorted_ppdp:
                if total_load < peak_load:
                    total_load += ppdp.amount
                    clearing_price = ppdp.price

            self.reps.create_market_clearingpoint(market.name, clearing_price, total_load)
