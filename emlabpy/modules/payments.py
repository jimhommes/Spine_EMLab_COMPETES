from modules.defaultmodule import DefaultModule
from util.repository import Repository


class PayAndBankCO2Allowances(DefaultModule):
    def __init__(self, reps: Repository):
        super().__init__("Payment Module: CO2 Payments and Banking", reps)

    def act(self):
        for power_plant in self.reps.power_plants.values():
            market = self.reps.get_co2_market_for_plant(power_plant)
            mcp = self.reps.get_market_clearing_point_for_market_and_time(market, self.reps.current_tick)

            total_capacity = self.reps.get_total_accepted_amounts_by_power_plant_and_tick(power_plant,
                                                                                          self.reps.current_tick)
            emission_intensity = power_plant.calculate_emission_intensity(self.reps)
            emissions = total_capacity * emission_intensity

            if 1.5 * emissions * mcp.price <= int(power_plant.owner.parameters['cash']):
                power_plant.owner.parameters['cash'] = int(power_plant.owner.parameters['cash']) - 1.5 * emissions * mcp.price
                power_plant.banked_allowances += 1.5 * emissions
            elif emissions * mcp.price <= int(power_plant.owner.parameters['cash']):
                power_plant.owner.parameters['cash'] = int(power_plant.owner.parameters['cash']) - emissions * mcp.price
                power_plant.banked_allowances += emissions
            elif power_plant.banked_allowances < emissions and \
                    (power_plant.owner.banked_allowances - emissions) * mcp.price <= int(power_plant.owner.parameters['cash']):
                power_plant.parameters['cash'] = int(power_plant.parameters['cash']) - (power_plant.banked_allowances - emissions) * mcp.price
                power_plant.banked_allowances += (power_plant.banked_allowances - emissions)
            self.reps.dbrw.stage_payment_co2_allowances(power_plant, int(power_plant.owner.parameters['cash']),
                                                        power_plant.banked_allowances, self.reps.current_tick)
