from domain.energy import PowerPlant
from util.repository import Repository


class TestPowerPlant:

    def test_get_load_factor_for_production(self, reps: Repository):
        pp1 = reps.power_plants['Power Plant 1']
        assert pp1.get_load_factor_for_production(485 * 2) == 2

    def test_calculate_emission_intensity(self, reps: Repository):
        pp1 = reps.power_plants['Power Plant 1']    # Nuclear
        pp2 = reps.power_plants['Power Plant 2']    # CCGT
        assert pp1.calculate_emission_intensity(reps) == 0
        assert pp2.calculate_emission_intensity(reps) == 1 / (0.64 * 36) * 0.00187

    def test_get_actual_fixed_operating_cost(self, reps: Repository):
        pp1 = reps.power_plants['Power Plant 1']
        assert pp1.get_actual_fixed_operating_cost() == reps.power_generating_technologies['Nuclear PGT']\
            .get_fixed_operating_cost(-37 + 5 + 2) * 485

    def test_get_actual_nominal_capacity(self, reps: Repository):
        pp1 = reps.power_plants['Power Plant 1']
        assert pp1.get_actual_nominal_capacity() == 485
        pp_test = PowerPlant("newpp")
        pp_test.capacity = 0
        pp_test.location = reps.power_grid_nodes['nlNode']
        pp_test.technology = reps.power_generating_technologies['Coal PSC']
        assert pp_test.get_actual_nominal_capacity() == 750 * 1

    def test_calculate_marginal_fuel_cost(self, reps):
        pp1 = reps.power_plants['Power Plant 1']
        assert pp1.calculate_marginal_fuel_cost_per_mw_by_tick(reps, 0) == 1 / (0.33 * 3800000000) * 5000000

    def test_calculate_co2_tax_marginal_cost(self, reps):
        # 0 because tax has been set to 0
        assert reps.power_plants['Power Plant 1'].calculate_co2_tax_marginal_cost(reps) == 0

    def test_calculate_marginal_cost_excl_co2_market_cost(self, reps):
        pp1 = reps.power_plants['Power Plant 1']
        assert pp1.calculate_marginal_cost_excl_co2_market_cost(reps, 0) == \
               pp1.calculate_marginal_fuel_cost_per_mw_by_tick(reps, 0)

