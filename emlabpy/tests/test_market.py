from domain.markets import SlopingDemandCurve
from util.repository import Repository


class TestMarket:

    def test_get_sloping_demand_curve(self, reps: Repository):
        cm1 = reps.capacity_markets['DutchCapacityMarket']
        assert isinstance(cm1.get_sloping_demand_curve(0), SlopingDemandCurve)

    def test_get_price_at_volume(self, reps: Repository):  # From sloping demand curve
        irm = 1
        lm = 0.1
        d_peak = 1
        lm_volume = d_peak * (1 + irm - lm)
        um = 0.9
        um_volume = d_peak * (1 + irm + um)
        price_cap = 100
        scp = SlopingDemandCurve(irm, lm, um, d_peak, price_cap)
        assert scp.get_price_at_volume(0) == price_cap    # Hit price_cap
        assert scp.get_price_at_volume(5) == price_cap - price_cap / (um_volume - lm_volume)
        assert scp.get_price_at_volume(100) == 0

