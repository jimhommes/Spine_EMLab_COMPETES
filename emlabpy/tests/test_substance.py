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


class TestSubstance:

    def test_get_price_for_tick(self):
        pass

