#
# The file responsible for clearing the capacity market.
#
# Jim Hommes - 25-3-2021
#
import json


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
