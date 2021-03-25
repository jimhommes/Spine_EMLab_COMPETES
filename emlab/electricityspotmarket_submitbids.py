#
# Submit all offers to the electricity spot market.
# Based on EM-Lab's SubmitOffersToElectricitySpotMarketRole
#
# Jim Hommes - 25-3-2021
#

from datetime import datetime


class ElectricitySpotMarketSubmitBids:

    def __init__(self, reps, spinedb_reader_writer):
        self.reps = reps
        self.db = spinedb_reader_writer

        spinedb_reader_writer.import_object_class(spinedb_reader_writer.ppdp_object_class_name)
        spinedb_reader_writer.import_parameters(spinedb_reader_writer.ppdp_object_class_name,
                                                ['Market', 'Price', 'Capacity', 'EnergyProducer'])

    def act(self):
        # For every energy producer we will submit bids to the Capacity Market
        for energyProducer in self.reps.energyProducers.values():
            market = self.reps.electricitySpotMarkets[energyProducer.parameters['investorMarket']]

            # For every plant owned by energyProducer
            for powerPlant in self.reps.get_powerplants_by_owner(energyProducer.name):
                self.db.import_object(self.db.ppdp_object_class_name, powerPlant.name)

                # Calculate marginal cost mc
                #   fuelConsumptionPerMWhElectricityProduced = 3600 / (pp.efficiency * ss.energydensity)
                #   lastKnownFuelPrice
                substances = self.reps.get_substances_by_powerplant(powerPlant.name)
                if len(substances) > 0:  # Only done for 1 substance atm
                    mc = 3600 / (float(powerPlant.parameters['Efficiency']) * float(
                        substances[0].parameters['energyDensity']))
                    capacity = int(powerPlant.parameters['Capacity'])
                    self.reps.create_powerplant_dispatch_plan(powerPlant, energyProducer, market, capacity, mc)

                    self.db.import_object_parameter_values(self.db.ppdp_object_class_name, powerPlant.name,
                                                           [('Market', market.name), ('Price', mc),
                                                            ('Capacity', capacity),
                                                            ('EnergyProducer', energyProducer.name)])

        self.db.commit('EM-Lab Capacity Market: Submit Bids: ' + str(datetime.now()))
