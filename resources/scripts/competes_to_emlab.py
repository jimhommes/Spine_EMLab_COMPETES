"""
This script handles all communication passed from the COMPETES Excel output to the EM-Lab SpineDB.
It handles the MarketClearingPoint from the Hourly Nodal Prices and the unit generation as PowerPlantDispatchPlans.

Jim Hommes - 10-6-2021
"""
from spinedb import *
import sys
import pandas
from datetime import datetime

print('===== Starting COMPETES to EMLab script =====')
print('Loading Databases...')
db_emlab = SpineDB(sys.argv[1])
db_emlab_data = db_emlab.export_data()
print('Done loading Databases.')

print('Loading current EM-Lab tick...')
current_emlab_tick = max(
    [int(i[3]) for i in db_emlab_data['object_parameter_values'] if i[0] == i[1] == 'SystemClockTicks' and
     i[2] == 'ticks'])
current_competes_tick = 2020 + round(current_emlab_tick / 5) * 5
print('Current EM-Lab tick is ' + str(current_emlab_tick) +
      ', which translates to COMPETES tick ' + str(current_competes_tick))

path_to_competes_results = sys.argv[2]
file_name = sys.argv[3].replace('?', str(current_competes_tick))
print('Loading "Hourly Nodal Prices" Excel sheet...')
hourly_nodal_prices_df = pandas.read_excel(path_to_competes_results + '/' + file_name, 'Hourly Nodal Prices')
hourly_nodal_prices_df.columns = hourly_nodal_prices_df.iloc[0]
hourly_nodal_prices_df.drop([0])
print('Done')
hourly_nodal_prices_nl = hourly_nodal_prices_df['NED'][1:].values
hourly_nodal_prices_nl_avg = sum(hourly_nodal_prices_nl) / len(hourly_nodal_prices_nl)
print('Average hourly nodal prices: ' + str(hourly_nodal_prices_nl_avg))

print('Exporting MarketClearingPrice...')
newobject_mcp_name = 'MarketClearingPoint ' + str(datetime.now())
values = [('Market', 'DutchElectricitySpotMarket'), ('Price', hourly_nodal_prices_nl_avg)]
db_emlab.import_objects([('MarketClearingPoints', newobject_mcp_name)])
db_emlab.import_object_parameter_values([('MarketClearingPoints', newobject_mcp_name, i[0], i[1], str(current_emlab_tick))
                                         for i in values])
print('Done')

print('Loading "NL Unit Generation" Excel sheet...')
unit_generation_df = pandas.read_excel(path_to_competes_results + '/' + file_name, 'NL Unit Generation', index_col=0, skiprows=1)
unit_generation_df = unit_generation_df.transpose()
ppdp_objects_to_import = []
ppdp_values_to_import = []
for power_plant in unit_generation_df.columns:
    print('Staging PPDP for ' + str(power_plant))
    accepted = sum(unit_generation_df[power_plant].values)
    ppdp_name = 'PowerPlantDispatchPlan ' + str(datetime.now())
    ppdp_objects_to_import.append(('PowerPlantDispatchPlans', ppdp_name))
    owner = next(i[3] for i in db_emlab_data['object_parameter_values'] if i[0] == 'PowerPlants' and i[1] == power_plant and i[2] == 'FirmNL')
    status = 'Accepted' if accepted > 0 else 'Failed'
    values = [('AcceptedAmount', accepted), ('Capacity', accepted), ('EnergyProducer', owner), ('Market', 'DutchElectricitySpotMarket'), ('Plant', power_plant), ('Status', status), ('Price', hourly_nodal_prices_nl_avg)]
    ppdp_values_to_import = ppdp_values_to_import + [('PowerPlantDispatchPlans', ppdp_name, i[0], i[1], str(current_emlab_tick)) for i in values]
db_emlab.import_objects(ppdp_objects_to_import)
db_emlab.import_object_parameter_values(ppdp_values_to_import)

print('Done')

print('Exporting PowerPlantDispatchPlans...')


print('Done')

print('Committing...')
db_emlab.commit('Imported from COMPETES')
print('Done')

db_emlab.close_connection()



