"""
This script handles all communication passed from the EM-Lab SpineDB to the COMPETES SpineDB.
As of this moment this only entails the CO2 Price.

Jim Hommes - 1-6-2021
"""
import sys

from spinedb import SpineDB

print('===== Starting EMLab to COMPETES script =====')

print('Loading Databases...')
db_emlab = SpineDB(sys.argv[1])
db_emlab_data = db_emlab.export_data()
db_competes = SpineDB(sys.argv[2])
print('Done loading Databases.')

print('Loading current EM-Lab tick...')
current_emlab_tick = max(
    [int(i[3]) for i in db_emlab_data['object_parameter_values'] if i[0] == i[1] == 'SystemClockTicks' and
     i[2] == 'ticks'])
current_competes_tick = 2020 + round(current_emlab_tick / 5) * 5
print('Current EM-Lab tick is ' + str(current_emlab_tick) +
      ', which translates to COMPETES tick ' + str(current_competes_tick))

print('Creating structure...')
object_class_name = 'EU_ETS_CO2price'
print('Staging object class')
db_competes.import_object_classes([object_class_name])
print('Staging object')
db_competes.import_objects([(object_class_name, str(current_competes_tick))])
print('Staging object parameters')
parameters = ['Jan', 'Feb', 'March', 'April', 'May', 'June', 'July', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
db_competes.import_data({'object_parameters': [[object_class_name, i] for i in parameters]})

print('Loading CO2 MarketClearingPrice...')
mcp_lines = [i for i in db_emlab_data['object_parameter_values'] if i[0] == 'MarketClearingPoints'
             and i[4] == str(current_emlab_tick)]
mcp_object = next(i[1] for i in mcp_lines if i[2] == 'Market' and i[3] == 'CO2Auction')
mcp = next(float(i[3]) for i in mcp_lines if i[1] == mcp_object and i[2] == 'Price')
print('Price found: ' + str(mcp))

print('Staging prices...')
db_competes.import_object_parameter_values([(object_class_name, str(current_competes_tick), i, mcp) for i in parameters])

print('Committing...')
db_competes.commit('Committing CO2 Prices. EMLab tick: ' + str(current_emlab_tick) +
                   ', COMPETES tick: ' + str(current_competes_tick))
print('Done!')
print('===== End of EMLab to COMPETES script =====')



