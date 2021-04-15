"""
The file responsible for all CO2 Market classes.

Jim Hommes - 13-4-2021
"""
from modules.marketmodule import MarketModule


class CO2MarketDetermineCO2Price(MarketModule):

    def __init__(self, reps):
        super().__init__('CO2 Market: Determine CO2 Price', reps)

    def act(self):
        # TODO: Branch first tick (how to determine first price, without COMPETES run)
        # TODO: Read cap through trend
        # TODO: Get emissions from year 0
        # TODO: Get emissions from year 3
        # TODO: Calculate powerplant profits
        # TODO: Create merit order on WTP and determine CO2 Price
        for market in self.reps.co2_markets.values():
            co2price = 0
            if self.reps.current_tick == 0:     # If first tick, COMPETES has not run yet. Set to minprice
                zone = self.reps.zones[market.parameters['zone']]
            else:
                pass

