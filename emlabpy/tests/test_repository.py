from util.spinedb_reader_writer import *
from conftest import *
import pytest


class TestRepository:

    def test_get_power_plants_by_owner(self, reps):
        assert reps.get_power_plants_by_owner(reps.energy_producers['Energy Producer NL A']) == \
               [reps.power_plants['Power Plant 1']]

    def test_create_power_plant_dispatch_plan(self):
        pass

    def test_get_sorted_dispatch_plans_by_market(self):
        pass

    def test_create_market_clearing_point(self):
        pass

    def test_get_available_power_plant_capacity(self):
        pass

    def test_get_power_plant_dispatch_plans_by_plant(self):
        pass

    def test_get_power_plant_dispatch_plans_by_plant_and_tick(self):
        pass

    def test_set_power_plant_dispatch_plan_production(self):
        pass

    def test_get_electricity_spot_market_for_plant(self):
        pass

    def test_get_capacity_market_for_plant(self):
        pass

    def test_get_substances_in_fuel_mix_by_plant(self):
        pass

    def test_find_last_known_price_for_substance(self):
        pass

    def test_get_market_clearing_point_for_market_and_time(self):
        pass

    def test_get_market_clearing_point_price_for_market_and_time(self):
        pass

    def test_get_national_government_by_zone(self):
        pass

    def test_get_government(self):
        pass

    def test_get_power_plant_revenues_by_tick(self):
        pass

    def test_get_total_accepted_amounts_by_power_plant_and_tick(self):
        pass

    def test_get_power_plant_costs_by_tick(self):
        pass

    def test_get_power_plant_profits_by_tick(self):
        pass

    def test_get_power_plant_emissions_by_tick(self):
        pass
