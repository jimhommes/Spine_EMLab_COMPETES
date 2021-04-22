from util.repository import *

def get_shell_repo():
    repo = Repository()

    ep1 = EnergyProducer("EnergyProducer 1")
    ep2 = EnergyProducer("EnergyProducer 2")

    pp1 = PowerPlant("Powerplant 1")
    pp2 = PowerPlant("Powerplant 2")
    pp1.owner = ep1
    pp2.owner = ep2

    repo.power_plants[pp1.name] = pp1
    repo.power_plants[pp2.name] = pp2

    return repo


class TestPowerPlant:

    def test_get_load_factor_for_production(self):
        repo = get_shell_repo()
        pp1 = repo.power_plants['Powerplant 1']
        pp1.capacity = 1000

        assert pp1.get_load_factor_for_production(2000) == 2

    def test_calculate_emission_intensity(self):
        pass

    def test_get_actual_fixed_operating_cost(self):
        pass

    def test_get_actual_nominal_capacity(self):
        pass

    def test_calculate_marginal_fuel_cost(self):
        pass

    def test_calculate_co2_tax_marginal_cost(self):
        pass

    def test_calculate_marginal_cost_excl_co2_market_cost(self):
        pass

