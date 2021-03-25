#
# Submit all offers to the electricity spot market.
# Based on EM-Lab's SubmitOffersToElectricitySpotMarketRole
#
# Jim Hommes - 25-3-2021
#

from datetime import datetime


class ElectricitySpotMarketSubmitBids:

    def __init__(self, reps):
        self.reps = reps
        reps.dbrw.init_powerplantdispatchplan_structure()

    def act(self):
        # For every energy producer we will submit bids to the Capacity Market
        for energyProducer in self.reps.energyProducers.values():
            market = self.reps.electricitySpotMarkets[energyProducer.parameters['investorMarket']]

            # For every plant owned by energyProducer
            for powerPlant in self.reps.get_powerplants_by_owner(energyProducer.name):
                # Calculate marginal cost mc
                #   fuelConsumptionPerMWhElectricityProduced = 3600 / (pp.efficiency * ss.energydensity)
                #   lastKnownFuelPrice
                substances = self.reps.get_substances_by_powerplant(powerPlant.name)
                if len(substances) > 0:  # Only done for 1 substance atm
                    mc = 3600 / (float(powerPlant.parameters['Efficiency']) * float(
                        substances[0].parameters['energyDensity']))
                    capacity = int(powerPlant.parameters['Capacity'])
                    self.reps.create_powerplant_dispatch_plan(powerPlant, energyProducer, market, capacity, mc)
