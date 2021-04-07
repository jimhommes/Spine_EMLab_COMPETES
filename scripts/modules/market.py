"""
This is the parent class of all market modules.
The advantage of this parent class is that some calculations can be static as they are done for all market modules.

Jim Hommes - 7-4-2021
"""
from modules.defaultmodule import DefaultModule


class Market(DefaultModule):
    def calculate_marginal_fuel_cost(self, plant):
        fc = 0
        for substance_in_fuel_mix in self.reps.get_substances_in_fuel_mix_by_plant(plant.name):
            amount = substance_in_fuel_mix.share
            fuel_price = self.reps.find_last_known_price_for_substance(substance_in_fuel_mix.substance.name,
                                                                       self.reps.current_tick)
            fc += amount * fuel_price
        return fc

    def calculate_co2_tax_marginal_cost(self, plant):
        co2_intensity = plant.calculate_emission_intensity(self.reps)
        print('TODO: Implement government CO2 tax')
        #     co2_tax = government.get_co2_tax(tick)
        co2_tax = 1
        return co2_intensity * co2_tax

    def calculate_marginal_cost_excl_co2_market_cost(self, plant):
        mc = 0
        mc += self.calculate_marginal_fuel_cost(plant)
        mc += self.calculate_co2_tax_marginal_cost(plant)
        return mc
