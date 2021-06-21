"""
This script handles all communication passed from the EM-Lab SpineDB to the COMPETES SpineDB.
As of this moment this only entails the CO2 Price and Capacity Revenues.

Jim Hommes - 1-6-2021
"""
import sys
from spinedb import SpineDB

print('===== Starting EMLab to COMPETES script =====')

print('Loading Databases...')
db_emlab = SpineDB(sys.argv[1])
db_competes = SpineDB(sys.argv[2])
try:
    db_emlab_data = db_emlab.export_data()
    db_competes_data = db_competes.export_data()
    print('Done loading Databases.')

    print('Loading current EM-Lab tick...')
    current_emlab_tick = max(
        [int(i[3]) for i in db_emlab_data['object_parameter_values'] if i[0] == i[1] == 'SystemClockTicks' and
         i[2] == 'ticks'])
    current_competes_tick_rounded = 2020 + round(current_emlab_tick / 5) * 5
    current_competes_tick = 2020 + current_emlab_tick
    print('Current EM-Lab tick is ' + str(current_emlab_tick) +
          ', which translates to COMPETES tick ' + str(current_competes_tick) + ' or rounded '
          + str(current_competes_tick_rounded))

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
    db_competes.import_object_parameter_values([(object_class_name, str(current_competes_tick), i, mcp, '0') for i in parameters])

    if current_emlab_tick > 0:
        print('Getting CapacityMarket clearing price...')
        capacity_market_clearing_price = next(float(i[3]) for i in db_emlab_data['object_parameter_values'] if i[0] == 'MarketClearingPoints' and i[2] == 'Price' and i[4] == str(current_emlab_tick - 1))
        print('Capacity Market Clearing Price found: ' + str(capacity_market_clearing_price))

        print('Aggregating Capacity Market revenues per technology...')
        technology_total_revenue = {}
        for ppdp_object in [i[1] for i in db_emlab_data['objects'] if i[0] == 'PowerPlantDispatchPlans']:
            values = {i[2]: i[3] for i in db_emlab_data['object_parameter_values'] if i[0] == 'PowerPlantDispatchPlans' and i[1] == ppdp_object and i[4] == str(current_emlab_tick-1)}
            if 'Market' in values.keys() and values['Market'] == 'DutchCapacityMarket':
                unit = values['Plant']
                tech = next(i[3] for i in db_emlab_data['object_parameter_values'] if i[0] == 'PowerPlants' and i[1] == unit and i[2] == 'TECHTYPENL')
                revenue = float(values['AcceptedAmount']) * capacity_market_clearing_price
                try:
                    technology_total_revenue[tech] += revenue
                except KeyError:
                    technology_total_revenue[tech] = revenue

        print(technology_total_revenue)
        print('Done')

        print('Staging revenues as CAPEX reductions...')
        print('Part 1: Overnight costs')
        for tech in technology_total_revenue.keys():
            valuemap_per_fuel = next(i[3] for i in db_competes_data['object_parameter_values'] if i[0] == 'Overnight Cost (OC)' and i[1] == tech)
            param_name = next(i[2] for i in db_competes_data['object_parameter_values'] if i[0] == 'Overnight Cost (OC)' and i[1] == tech)
            print(tech)
            for valuemap_per_year in valuemap_per_fuel.values:
                i = valuemap_per_year.indexes.tolist().index(str(current_competes_tick))
                print('Old value: ' + str(valuemap_per_year.values[i]))
                valuemap_per_year.values[i] -= float(technology_total_revenue[tech])
                print('New value: ' + str(valuemap_per_year.values[i]))

            db_competes.import_data({'object_parameters': [('Overnight Cost (OC)', 'Overnight Cost (OC)')]})
            db_competes.import_object_parameter_values([('Overnight Cost (OC)', tech, param_name, valuemap_per_fuel, 0)])
        print('Done')

    print('Committing...')
    db_competes.commit('Committing CO2 Prices and Revenues. EMLab tick: ' + str(current_emlab_tick) +
                       ', COMPETES tick: ' + str(current_competes_tick))

    db_competes.close_connection()
    db_emlab.close_connection()
    print('Done!')
except Exception as e:
    print('Exception occurred: ' + str(e))
finally:
    print('Closing database connections...')
    db_emlab.close_connection()
    db_competes.close_connection()
    print('===== End of EMLab to COMPETES script =====')



