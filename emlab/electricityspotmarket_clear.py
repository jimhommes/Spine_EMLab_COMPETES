#
# Clearing the Electricity Spot Market.
# Based on the role ClearIterativeCO2AndElectricitySpotMarketTwoCountryRole
#
# Jim Hommes - 25-3-2021
#

import json
from datetime import datetime


class ElectricitySpotMarketClearing:

    def __init__(self, reps, spinedb_reader_writer):
        self.reps = reps
        self.db = spinedb_reader_writer

        spinedb_reader_writer.import_object_class(spinedb_reader_writer.mcp_object_class_name)
        spinedb_reader_writer.import_parameters(spinedb_reader_writer.mcp_object_class_name,
                                                ['Market', 'Price', 'TotalCapacity'])

    def act(self):
        # Calculate and submit Market Clearing Price
        peak_load = max(json.loads(self.reps.load['NL'].parameters['ldc'].to_database())['data'].values())
        for market in self.reps.electricitySpotMarkets.values():
            sorted_ppdp = self.reps.get_sorted_dispatch_plans_by_market(market.name)
            clearing_price = 0
            total_load = 0
            for ppdp in sorted_ppdp:
                if total_load < peak_load:
                    total_load += ppdp.amount
                    clearing_price = ppdp.price

            self.db.import_object(self.db.mcp_object_class_name, 'ClearingPoint')
            self.db.import_object_parameter_values(self.db.mcp_object_class_name, 'ClearingPoint',
                                                   [('Market', market.name), ('Price', clearing_price),
                                                    ('TotalCapacity', total_load)])

        self.db.commit('EM-Lab Capacity Market: Submit Clearing Point: ' + str(datetime.now()))
