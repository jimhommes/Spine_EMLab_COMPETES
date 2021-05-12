"""
The Repository: home of all objects that play a part in the model.
All objects are read through the SpineDBReader and stored in the Repository.

Jim Hommes - 25-3-2021
"""
from datetime import datetime
from typing import Optional

from domain.actors import *
from domain.energy import *
from domain.markets import *
from domain.trends import *
from domain.zones import *


class Repository:
    """
    The Repository class reads DB data at initialization and loads all objects and relationships
    Also provides all functions that require e.g. sorting
    """

    def __init__(self):
        self.dbrw = None

        self.current_tick = 0

        self.energy_producers = dict()
        self.power_plants = dict()
        self.substances = dict()
        self.power_plants_fuel_mix = dict()
        self.electricity_spot_markets = dict()
        self.capacity_markets = dict()
        self.co2_markets = dict()
        self.power_plant_dispatch_plans = dict()
        self.power_generating_technologies = dict()
        self.load = dict()
        self.market_clearing_points = dict()
        self.power_grid_nodes = dict()
        self.trends = dict()
        self.zones = dict()
        self.national_governments = dict()
        self.governments = dict()
        self.market_stability_reserves = dict()

        self.power_plant_dispatch_plan_status_accepted = 'Accepted'
        self.power_plant_dispatch_plan_status_failed = 'Failed'
        self.power_plant_dispatch_plan_status_partly_accepted = 'Partly Accepted'
        self.power_plant_dispatch_plan_status_awaiting = 'Awaiting'

    def get_power_plants_by_owner(self, owner: EnergyProducer) -> list:
        return [i for i in self.power_plants.values() if i.owner == owner]

    def create_or_update_power_plant_dispatch_plan(self, plant: PowerPlant,
                                                   bidder: EnergyProducer,
                                                   bidding_market: Market,
                                                   amount: float,
                                                   price: float,
                                                   time: int) -> PowerPlantDispatchPlan:
        ppdp = next((ppdp for ppdp in self.power_plant_dispatch_plans.values() if ppdp.plant == plant and
                     ppdp.bidding_market == bidding_market and
                     ppdp.tick == time), None)
        if ppdp is None:
            # PowerPlantDispatchPlan not found, so create a new one
            name = 'PowerPlantDispatchPlan ' + str(datetime.now())
            ppdp = PowerPlantDispatchPlan(name)

        ppdp.plant = plant
        ppdp.bidder = bidder
        ppdp.bidding_market = bidding_market
        ppdp.amount = amount
        ppdp.price = price
        ppdp.status = self.power_plant_dispatch_plan_status_awaiting
        ppdp.accepted_amount = 0
        ppdp.tick = time

        self.power_plant_dispatch_plans[ppdp.name] = ppdp
        self.dbrw.stage_power_plant_dispatch_plan(ppdp, time)
        return ppdp

    def get_sorted_dispatch_plans_by_market_and_time(self, market: Market, time: int) -> list:
        return sorted([i for i in self.power_plant_dispatch_plans.values()
                       if i.bidding_market == market and i.tick == time], key=lambda i: i.price)

    def create_or_update_market_clearing_point(self,
                                               market: Market,
                                               price: float,
                                               capacity: float,
                                               time: int) -> MarketClearingPoint:
        mcp = next((mcp for mcp in self.market_clearing_points.values() if mcp.market == market and mcp.tick == time),
                   None)
        if mcp is None:
            # MarketClearingPoint not found, so create a new one
            name = 'MarketClearingPoint ' + str(datetime.now())
            mcp = MarketClearingPoint(name)

        mcp.market = market
        mcp.price = price
        mcp.capacity = capacity
        mcp.tick = time
        self.market_clearing_points[mcp.name] = mcp
        self.dbrw.stage_market_clearing_point(mcp, time)
        return mcp

    def get_available_power_plant_capacity_at_tick(self, plant: PowerPlant, current_tick: int) -> float:
        ppdps_sum_accepted_amount = sum([float(i.accepted_amount) for i in
                                         self.get_power_plant_dispatch_plans_by_plant(plant)
                                         if i.tick == current_tick])
        return plant.capacity - ppdps_sum_accepted_amount

    def get_power_plant_dispatch_plans_by_plant(self, plant: PowerPlant) -> list:
        return [i for i in self.power_plant_dispatch_plans.values() if i.plant == plant]

    def get_power_plant_dispatch_plans_by_plant_and_tick(self, plant: PowerPlant, time: int) -> list:
        return [i for i in self.power_plant_dispatch_plans.values() if i.plant == plant and i.tick == time]

    def set_power_plant_dispatch_plan_production(self,
                                                 ppdp: PowerPlantDispatchPlan,
                                                 status: str, accepted_amount: float):
        ppdp.status = status
        ppdp.accepted_amount = accepted_amount
        self.dbrw.stage_power_plant_dispatch_plan(ppdp, self.current_tick)

    def get_electricity_spot_market_for_plant(self, plant: PowerPlant) -> ElectricitySpotMarket:
        zone = plant.location.parameters['Zone']
        res = [i for i in self.electricity_spot_markets.values() if i.parameters['zone'] == zone]
        if len(res) > 0:
            return res[0]

    def get_capacity_market_for_plant(self, plant: PowerPlant) -> CapacityMarket:
        zone = plant.location.parameters['Zone']
        res = [i for i in self.capacity_markets.values() if i.parameters['zone'] == zone]
        if len(res) > 0:
            return res[0]

    def get_substances_in_fuel_mix_by_plant(self, plant: PowerPlant) -> list:
        if plant.technology.name in self.power_plants_fuel_mix.keys():
            return self.power_plants_fuel_mix[plant.technology.name]
        else:
            return []

    def get_market_clearing_point_for_market_and_time(self, market: Market, time: int) -> Optional[MarketClearingPoint]:
        try:
            return next(i for i in self.market_clearing_points.values() if i.market == market and i.tick == time)
        except StopIteration:
            return None

    def get_market_clearing_point_price_for_market_and_time(self, market: Market, time: int) -> float:
        if time >= 0:
            mcp = self.get_market_clearing_point_for_market_and_time(market, time)
            return mcp.price
        else:
            return 0

    def get_national_government_by_zone(self, zone: Zone) -> NationalGovernment:
        return next(i for i in self.national_governments.values() if i.governed_zone == zone)

    def get_government(self) -> Government:
        return next(i for i in self.governments.values())

    def get_power_plant_electricity_spot_market_revenues_by_tick(self, power_plant: PowerPlant, time: int) -> float:
        return sum([float(
            i.accepted_amount * self.get_market_clearing_point_for_market_and_time(i.bidding_market, time).price
        )
            for i in self.get_power_plant_dispatch_plans_by_plant_and_tick(power_plant, time)])

    def get_total_accepted_amounts_by_power_plant_and_tick(self, power_plant: PowerPlant, time: int) -> float:
        return sum([i.accepted_amount for i in self.power_plant_dispatch_plans.values() if i.tick == time and
                    i.plant == power_plant])

    def get_power_plant_costs_by_tick(self, power_plant: PowerPlant, time: int) -> float:
        mc = power_plant.calculate_marginal_cost_excl_co2_market_cost(self, time)
        foc = power_plant.get_actual_fixed_operating_cost() / 8760  # TODO: Fix right timing
        total_capacity = self.get_total_accepted_amounts_by_power_plant_and_tick(power_plant, time)
        return foc + mc * total_capacity

    def get_power_plant_electricity_spot_market_profits_by_tick(self, time: int) -> dict:
        res = {}
        for power_plant in self.power_plants.values():
            revenues = self.get_power_plant_electricity_spot_market_revenues_by_tick(power_plant, time)
            costs = self.get_power_plant_costs_by_tick(power_plant, time)
            res[power_plant.name] = revenues - costs
        return res

    def get_power_plant_emissions_by_tick(self, time: int) -> dict:
        res = {}
        for power_plant in self.power_plants.values():
            total_capacity = self.get_total_accepted_amounts_by_power_plant_and_tick(power_plant, time)
            emission_intensity = power_plant.calculate_emission_intensity(self)
            res[power_plant.name] = total_capacity * emission_intensity
        return res

    def get_allowances_in_circulation(self, time: int) -> int:
        return sum([i.banked_allowances[time] for i in self.power_plants.values()])

    def get_co2_market_for_zone(self, zone: Zone):
        try:
            return next(i for i in self.co2_markets.values()
                        if i.parameters['zone'] == self.power_grid_nodes[zone.name].parameters['Zone'])
        except StopIteration:
            return None

    def get_co2_market_for_plant(self, power_plant: PowerPlant):
        return self.get_co2_market_for_zone(power_plant.location)
