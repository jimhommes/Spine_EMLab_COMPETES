from domain.import_object import *


class Market(ImportObject):
    pass


class ElectricitySpotMarket(Market):
    pass


class CapacityMarket(Market):

    def __init__(self, name: str):
        super().__init__(name)
        self.sloping_demand_curve = None

    def get_sloping_demand_curve(self, d_peak):
        return SlopingDemandCurve(float(self.parameters['InstalledReserveMargin']),
                                  float(self.parameters['LowerMargin']),
                                  float(self.parameters['UpperMargin']), d_peak, float(self.parameters['PriceCap']))


class CO2Market(Market):
    pass


class MarketClearingPoint(ImportObject):
    def __init__(self, name):
        super().__init__(name)
        self.market = None
        self.price = 0
        self.capacity = 0
        self.tick = -1

    def add_parameter_value(self, reps, parameter_name, parameter_value, alternative):
        self.tick = int(alternative)
        if parameter_name == 'Price':
            self.price = float(parameter_value)
        if parameter_name == 'Market':
            if parameter_value in reps.capacity_markets.keys():
                self.market = reps.capacity_markets[parameter_value]
            else:
                self.market = reps.electricity_spot_markets[parameter_value]
        if parameter_name == 'TotalCapacity':
            self.capacity = float(parameter_value)


class SlopingDemandCurve:
    def __init__(self, irm, lm, um, d_peak, price_cap):
        self.irm = irm
        self.lm = lm
        self.lm_volume = d_peak * (1 + irm - lm)
        self.um = um
        self.um_volume = d_peak * (1 + irm + um)
        self.d_peak = d_peak
        self.price_cap = price_cap

    def get_price_at_volume(self, volume):
        m = self.price_cap / (self.um_volume - self.lm_volume)
        if volume < self.lm_volume:
            return self.price_cap
        elif self.lm_volume <= volume <= self.um_volume:
            return self.price_cap - m * (volume - self.lm_volume)
        elif self.um_volume < volume:
            return 0
