"""
The file responsible for all CO2 Market classes.

Jim Hommes - 13-4-2021
"""
from modules.marketmodule import MarketModule
from util.repository import Repository


class CO2MarketDetermineCO2Price(MarketModule):
    """
    This class determines the CO2 Price based on the Willingness To Pay of the PowerPlants.
    It does so by evaluating the profits and emissions of last year.
    """

    def __init__(self, reps: Repository):
        super().__init__('CO2 Market: Determine CO2 Price', reps)
        reps.dbrw.stage_init_market_clearing_point_structure()

    def act(self):
        # For every CO2Market
        for market in self.reps.co2_markets.values():
            co2price = 0
            if self.reps.current_tick == 0:
                # If first tick, COMPETES has not run yet. Set to CO2 substance cost
                # co2price = self.reps.substances['co2'].get_price_for_tick(0)
                co2price = 40
            #     TODO: What to do with the first CO2 price?
            else:
                # If not first tick, base CO2 Price of profits/emissions last year

                # If implemented, take MarketStabilityReserve into account
                msr = self.reps.get_market_stability_reserve_for_market(market)
                if msr is not None:
                    co2_cap = self.reps.get_government().co2_cap_trend.get_value(self.reps.current_tick - 1) / 8760 - \
                              self.reps.get_allowances_in_circulation(self.reps.zones[market.parameters['zone']], self.reps.current_tick)\
                              + msr.flow
                else:
                    co2_cap = self.reps.get_government().co2_cap_trend.get_value(self.reps.current_tick - 1) / 8760 - \
                              self.reps.get_allowances_in_circulation(self.reps.zones[market.parameters['zone']], self.reps.current_tick)

                # Get profits, emissions and calculate WTP
                profits_per_plant = self.reps.get_power_plant_electricity_spot_market_profits_by_tick(
                    self.reps.current_tick - 1)
                emissions_per_plant = self.reps.get_power_plant_emissions_by_tick(self.reps.current_tick - 1)
                willingness_to_pay_per_plant = {
                    key: value / emissions_per_plant[key] if emissions_per_plant[key] != 0 else value for (key, value)
                    in profits_per_plant.items()
                }

                # Determine CO2 Price based on the WTP merit order
                co2price = max(willingness_to_pay_per_plant.values())
                total_emissions = 0
                for (power_plant_name, wtp) in sorted(willingness_to_pay_per_plant.items(),
                                                      key=lambda item: item[1], reverse=True):
                    plant = self.reps.power_plants[power_plant_name]
                    if co2_cap >= total_emissions + emissions_per_plant[power_plant_name]:
                        total_emissions += emissions_per_plant[power_plant_name]
                        co2price = wtp
                    else:
                        break

            # Check if CO2Price is below the Government's min CO2 price
            co2price = self.floor_co2price(co2price)
            self.reps.create_or_update_market_clearing_point(market, co2price, 0, self.reps.current_tick)

    def floor_co2price(self, co2price):
        """Check if CO2Price is below the Government's min CO2 price"""
        return max(co2price, self.reps.get_government().co2_min_price_trend.get_value(self.reps.current_tick))
