"""
The file responsible for all CO2 Market classes.

Jim Hommes - 13-4-2021
"""
from modules.marketmodule import MarketModule


class CO2MarketDetermineCO2Price(MarketModule):

    def __init__(self, reps):
        super().__init__('CO2 Market: Determine CO2 Price', reps)

    def act(self):
        # TODO: Get emissions from year 0
        # TODO: Get emissions from year 3
        # TODO: Create merit order on WTP and determine CO2 Price
        for market in self.reps.co2_markets.values():
            print('yes')
            co2price = 0
            if self.reps.current_tick == 0:     # If first tick, COMPETES has not run yet. Set to minprice
                zone = self.reps.zones[market.parameters['zone']]
                national_government = self.reps.get_national_government_by_zone(zone)
                co2price = national_government.trend.get_value(self.reps.current_tick)
            else:
                co2_cap = self.reps.get_government().co2_cap_trend.get_value(self.reps.current_tick)
                profits_per_plant = self.reps.get_power_plant_profits_by_tick(self.reps.current_tick)
                emissions_per_plant = self.reps.get_power_plant_emissions_by_tick(self.reps.current_tick)
                willingness_to_pay_per_plant = {
                    key: value / emissions_per_plant[key] if emissions_per_plant[key] != 0 else value for (key, value)
                    in profits_per_plant.items()}

                co2price = max(willingness_to_pay_per_plant.values())
                total_emissions = 0
                for (power_plant_name, wtp) in sorted(willingness_to_pay_per_plant.items(), key=lambda item: item[1]):
                    plant = self.reps.power_plants[power_plant_name]
                    if co2_cap >= total_emissions + emissions_per_plant[power_plant_name]:
                        total_emissions += emissions_per_plant[power_plant_name]
                        co2price = willingness_to_pay_per_plant[power_plant_name]

                print(co2price)
