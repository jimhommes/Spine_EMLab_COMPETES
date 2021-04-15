"""
The file responsible for all CO2 Market classes.

Jim Hommes - 13-4-2021
"""
from modules.market import Market


class CO2MarketDetermineCO2Price(Market):

    def __init__(self, reps):
        super().__init__('CO2 Market: Determine CO2 Price', reps)

    def act(self):
        # TODO: Branch first tick (how to determine first price, without COMPETES run)
        # TODO: Read cap through trend
        # TODO: Get emissions from year 0
        # TODO: Get emissions from year 3
        # TODO: Calculate powerplant profits
        # TODO: Create merit order on WTP and determine CO2 Price
        pass
