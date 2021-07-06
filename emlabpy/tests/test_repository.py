from conftest import *
from domain.actors import *

class TestRepository:

    def test_get_power_plants_by_owner(self, reps):
        assert reps.get_operational_power_plants_by_owner(reps.energy_producers['Energy Producer NL A']) == \
               [reps.power_plants['Power Plant 1']]

    def test_create_power_plant_dispatch_plan(self, reps, mocker):
        spy = mocker.spy(reps.dbrw, 'stage_power_plant_dispatch_plan')

        previous_size = len(reps.power_plant_dispatch_plans.keys())
        reps.create_or_update_power_plant_dispatch_plan(PowerPlant("newpp"),
                                                        EnergyProducer("newbidder"),
                                                        ElectricitySpotMarket("newesm"),
                                                        10, 20)
        assert len(reps.power_plant_dispatch_plans.keys()) == previous_size + 1
        assert reps.power_plant_dispatch_plans[sorted(reps.power_plant_dispatch_plans.keys())[0]].plant.name == 'newpp'
        assert spy.call_count == 1

    def test_get_sorted_dispatch_plans_by_market(self, reps: Repository):
        esm = reps.electricity_spot_markets['DutchElectricitySpotMarket']
        ppdp1 = reps.create_or_update_power_plant_dispatch_plan(PowerPlant("newpp1"),
                                                                EnergyProducer("newbidder1"),
                                                                esm,
                                                                100, 10)
        ppdp2 = reps.create_or_update_power_plant_dispatch_plan(PowerPlant("newpp2"),
                                                                EnergyProducer("newbidder1"),
                                                                esm,
                                                                100, 20)
        ppdp3 = reps.create_or_update_power_plant_dispatch_plan(PowerPlant("newpp3"),
                                                                EnergyProducer("newbidder1"),
                                                                esm,
                                                                100, 30)
        ppdp4 = reps.create_or_update_power_plant_dispatch_plan(PowerPlant("newpp4"),
                                                                EnergyProducer("newbidder1"),
                                                                esm,
                                                                100, 5)
        ppdp5 = reps.create_or_update_power_plant_dispatch_plan(PowerPlant("newpp5"),
                                                                EnergyProducer("newbidder1"),
                                                                esm,
                                                                100, 60)
        assert reps.get_sorted_power_plant_dispatch_plans_by_market_and_time(esm) == [ppdp4, ppdp1, ppdp2, ppdp3, ppdp5]

    def test_create_market_clearing_point(self, reps: Repository, mocker):
        spy = mocker.spy(reps.dbrw, 'stage_market_clearing_point')
        previous_size = len(reps.market_clearing_points)
        reps.create_or_update_market_clearing_point(ElectricitySpotMarket("newmarket"),
                                                    10, 20)
        assert len(reps.market_clearing_points) == previous_size + 1
        assert reps.market_clearing_points[sorted(reps.market_clearing_points.keys())[0]].market == 'newmarket'
        assert spy.call_count == 1

    def test_get_available_power_plant_capacity_at_tick(self, reps: Repository):
        reps.current_tick = 0
        plant = reps.power_plants['Power Plant 1']
        market = reps.electricity_spot_markets['DutchElectricitySpotMarket']
        reps.create_or_update_power_plant_dispatch_plan(plant, plant.owner, market, 100, 1)
        reps.create_or_update_power_plant_dispatch_plan(plant, plant.owner, market, 20, 1)
        reps.current_tick = 1
        reps.create_or_update_power_plant_dispatch_plan(plant, plant.owner, market, 300, 1)

        # Accept all plans
        for ppdp in reps.power_plant_dispatch_plans.values():
            ppdp.status = reps.power_plant_dispatch_plan_status_accepted
            ppdp.accepted_amount = ppdp.amount

        assert reps.get_available_power_plant_capacity_at_tick(plant, 0) == plant.capacity - 100 - 20
        assert reps.get_available_power_plant_capacity_at_tick(plant, 1) == plant.capacity - 300

    def test_get_power_plant_dispatch_plans_by_plant(self, reps: Repository):
        plant = PowerPlant("new plant test 1")
        ppdp1 = PowerPlantDispatchPlan('ppdp1')
        ppdp2 = PowerPlantDispatchPlan('ppdp2')
        ppdp1.plant = plant
        ppdp2.plant = plant
        reps.power_plant_dispatch_plans[ppdp1.name] = ppdp1
        reps.power_plant_dispatch_plans[ppdp2.name] = ppdp2
        assert reps.get_power_plant_dispatch_plans_by_plant(plant) == [ppdp1, ppdp2]

    def test_get_power_plant_dispatch_plans_by_plant_and_tick(self, reps: Repository):
        plant = PowerPlant("new plant test 1")
        ppdp1 = PowerPlantDispatchPlan('ppdp1')
        ppdp2 = PowerPlantDispatchPlan('ppdp2')
        ppdp1.plant = plant
        ppdp2.plant = plant
        reps.power_plant_dispatch_plans[ppdp1.name] = ppdp1
        reps.power_plant_dispatch_plans[ppdp2.name] = ppdp2
        ppdp1.tick = 20
        ppdp2.tick = 21
        assert reps.get_power_plant_dispatch_plans_by_plant_and_tick(plant, 20) == [ppdp1]
        assert reps.get_power_plant_dispatch_plans_by_plant_and_tick(plant, 21) == [ppdp2]

    def test_set_power_plant_dispatch_plan_production(self, reps: Repository, mocker):
        spy = mocker.spy(reps.dbrw, 'stage_power_plant_dispatch_plan')
        ppdp = PowerPlantDispatchPlan("newppdp")
        ppdp.plant = PowerPlant("newplant")
        ppdp.bidding_market = ElectricitySpotMarket("newmarket")
        ppdp.price = 10
        ppdp.amount = 100
        ppdp.bidder = EnergyProducer("newproducer")
        reps.set_power_plant_dispatch_plan_production(ppdp, reps.power_plant_dispatch_plan_status_accepted, 100)

        assert ppdp.status == reps.power_plant_dispatch_plan_status_accepted
        assert ppdp.accepted_amount == 100
        assert spy.call_count == 1

    def test_get_electricity_spot_market_for_plant(self, reps: Repository):
        assert reps.get_electricity_spot_market_for_plant(reps.power_plants['Power Plant 1']) == \
               reps.electricity_spot_markets['DutchElectricitySpotMarket']

    def test_get_capacity_market_for_plant(self, reps: Repository):
        assert reps.get_capacity_market_for_plant(reps.power_plants['Power Plant 1']) == \
               reps.capacity_markets['DutchCapacityMarket']

    def test_get_substances_in_fuel_mix_by_plant(self, reps: Repository):
        assert reps.get_substances_in_fuel_mix_by_plant(reps.power_plants['Power Plant 1']) == \
               reps.power_plants_fuel_mix['Nuclear PGT']

    def test_get_market_clearing_point_for_market_and_time(self, reps: Repository):
        market = ElectricitySpotMarket("testmarketforget")
        tick = 2019
        mcp1 = MarketClearingPoint("new")
        mcp1.market = market
        mcp1.tick = tick
        mcp1.price = 1234
        mcp3 = MarketClearingPoint("new3")
        reps.market_clearing_points[mcp1.name] = mcp1
        reps.market_clearing_points[mcp3.name] = mcp3
        assert reps.get_market_clearing_point_for_market_and_time(market, tick) == mcp1

    def test_get_market_clearing_point_price_for_market_and_time(self, reps: Repository):
        market = ElectricitySpotMarket("testmarketforget")
        tick = 2019
        mcp1 = MarketClearingPoint("new")
        mcp1.market = market
        mcp1.tick = tick
        mcp1.price = 1234
        mcp3 = MarketClearingPoint("new3")
        reps.market_clearing_points[mcp1.name] = mcp1
        reps.market_clearing_points[mcp3.name] = mcp3
        assert reps.get_market_clearing_point_price_for_market_and_time(market, tick) == 1234

    def test_get_national_government_by_zone(self, reps: Repository):
        assert reps.get_national_government_by_zone(reps.zones['nl']) == reps.national_governments['DutchGov']

    def test_get_government(self, reps: Repository):
        assert reps.get_government() == next(i for i in reps.governments.values())

    def test_get_power_plant_revenues_by_tick(self, reps: Repository):
        plant = PowerPlant("newplant")
        ppdp1 = PowerPlantDispatchPlan("ppdp1_for_revenues")
        ppdp2 = PowerPlantDispatchPlan("ppdp2_for_revenues")
        ppdp1.accepted_amount = 100
        ppdp1.price = 10
        ppdp1.plant = plant
        ppdp1.tick = 123
        ppdp2.accepted_amount = 200
        ppdp2.price = 5
        ppdp2.plant = plant
        ppdp2.tick = 123
        reps.power_plant_dispatch_plans[ppdp1.name] = ppdp1
        reps.power_plant_dispatch_plans[ppdp2.name] = ppdp2
        assert reps.get_power_plant_electricity_spot_market_revenues_by_tick(plant, 123) == 100 * 10 + 200 * 5

    def test_get_total_accepted_amounts_by_power_plant_and_tick(self, reps: Repository):
        plant = PowerPlant("newplant")
        ppdp1 = PowerPlantDispatchPlan("ppdp1_for_revenues")
        ppdp2 = PowerPlantDispatchPlan("ppdp2_for_revenues")
        ppdp1.accepted_amount = 100
        ppdp1.price = 10
        ppdp1.plant = plant
        ppdp1.tick = 123
        ppdp2.accepted_amount = 200
        ppdp2.price = 5
        ppdp2.plant = plant
        ppdp2.tick = 123
        reps.power_plant_dispatch_plans[ppdp1.name] = ppdp1
        reps.power_plant_dispatch_plans[ppdp2.name] = ppdp2
        assert reps.get_total_accepted_amounts_by_power_plant_and_tick(plant, 123) == 100 + 200

    def test_get_power_plant_costs_by_tick(self, reps: Repository):
        fuel_cost = 5000000 / (0.33 * 3800000000)
        fixed_operating_cost = pow(1 + 0.05, -37 + 2 + 5) * 71870 * 485
        accepted_capacity = reps.get_total_accepted_amounts_by_power_plant_and_tick(reps.power_plants['Power Plant 1'],
                                                                                    0)
        assert round(reps.get_power_plant_costs_by_tick(reps.power_plants['Power Plant 1'], 0), 3) == \
               round(fixed_operating_cost + fuel_cost * accepted_capacity, 3)

    def test_get_power_plant_profits_by_tick(self, reps: Repository):
        plant1 = reps.power_plants['Power Plant 1']
        plant2 = reps.power_plants['Power Plant 2']
        plant3 = reps.power_plants['Power Plant 3']
        plant4 = reps.power_plants['Power Plant 4']
        plant5 = reps.power_plants['Power Plant 5']

        profit_plant1 = reps.get_power_plant_electricity_spot_market_revenues_by_tick(plant1, 0) - reps.get_power_plant_costs_by_tick(plant1, 0)
        profit_plant2 = reps.get_power_plant_electricity_spot_market_revenues_by_tick(plant2, 0) - reps.get_power_plant_costs_by_tick(plant2, 0)
        profit_plant3 = reps.get_power_plant_electricity_spot_market_revenues_by_tick(plant3, 0) - reps.get_power_plant_costs_by_tick(plant3, 0)
        profit_plant4 = reps.get_power_plant_electricity_spot_market_revenues_by_tick(plant4, 0) - reps.get_power_plant_costs_by_tick(plant4, 0)
        profit_plant5 = reps.get_power_plant_electricity_spot_market_revenues_by_tick(plant5, 0) - reps.get_power_plant_costs_by_tick(plant5, 0)

        assert reps.get_power_plant_operational_profits_by_tick(0) == \
               {plant1.name: profit_plant1,
                plant2.name: profit_plant2,
                plant3.name: profit_plant3,
                plant4.name: profit_plant4,
                plant5.name: profit_plant5}

    def test_get_power_plant_emissions_by_tick(self, reps: Repository):
        plant1 = reps.power_plants['Power Plant 1']
        plant2 = reps.power_plants['Power Plant 2']
        plant3 = reps.power_plants['Power Plant 3']
        plant4 = reps.power_plants['Power Plant 4']
        plant5 = reps.power_plants['Power Plant 5']

        emission1 = plant1.get_load_factor_for_production(
            reps.get_total_accepted_amounts_by_power_plant_and_tick(plant1, 0)
        ) * plant1.calculate_emission_intensity(reps)
        emission2 = plant2.get_load_factor_for_production(
            reps.get_total_accepted_amounts_by_power_plant_and_tick(plant2, 0)
        ) * plant2.calculate_emission_intensity(reps)
        emission3 = plant3.get_load_factor_for_production(
            reps.get_total_accepted_amounts_by_power_plant_and_tick(plant3, 0)
        ) * plant3.calculate_emission_intensity(reps)
        emission4 = plant4.get_load_factor_for_production(
            reps.get_total_accepted_amounts_by_power_plant_and_tick(plant4, 0)
        ) * plant4.calculate_emission_intensity(reps)
        emission5 = plant5.get_load_factor_for_production(
            reps.get_total_accepted_amounts_by_power_plant_and_tick(plant5, 0)
        ) * plant5.calculate_emission_intensity(reps)

        assert reps.get_power_plant_emissions_by_tick(0) == {
            plant1.name: emission1,
            plant2.name: emission2,
            plant3.name: emission3,
            plant4.name: emission4,
            plant5.name: emission5
        }
