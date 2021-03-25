#
# The file responsible for submitting bids to the capacity market.
#
# Jim Hommes - 25-3-2021
#


class CapacityMarketSubmitBids:

    def __init__(self, reps):
        self.reps = reps

    def act(self):
        # For every energy producer we will submit bids to the Capacity Market
        for energyProducer in self.reps.energyProducers.values():
            market = self.reps.capacityMarkets[energyProducer.parameters['capacityMarket']]

            # For every plant owned by energyProducer
            for powerPlant in self.reps.get_powerplants_by_owner(energyProducer.name):
                # Calculate marginal cost mc
                #   fuelConsumptionPerMWhElectricityProduced = 3600 / (pp.efficiency * ss.energydensity)
                #   lastKnownFuelPrice
                substances = self.reps.get_substances_by_powerplant(powerPlant.name)
                if len(substances) > 0:  # Only done for 1 substance atm
                    mc = 3600 / (float(powerPlant.parameters['Efficiency']) * float(
                        substances[0].parameters['energyDensity']))
                    capacity = self.reps.get_available_powerplant_capacity(powerPlant.name)
                    if capacity == 0:
                        price_to_bid = 0
                    else:
                        price_to_bid = mc
                    self.reps.create_powerplant_dispatch_plan(powerPlant, energyProducer, market, capacity, price_to_bid)
