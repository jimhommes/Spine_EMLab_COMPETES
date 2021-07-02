"""
This script handles all communication passed from the EM-Lab SpineDB to the COMPETES SpineDB.
As of this moment this only entails the CO2 Price and Capacity Revenues.

Jim Hommes - 1-6-2021
"""
import sys
from spinedb import SpineDB
from helper_functions import get_current_ticks

print('===== Starting EMLab to COMPETES script =====')

print('Loading Databases...')
db_emlab = SpineDB(sys.argv[1])
db_competes = SpineDB(sys.argv[2])
try:
    current_emlab_tick, current_competes_tick, current_competes_tick_rounded = get_current_ticks(db_emlab, 2020)
    db_emlab_marketclearingpoints = db_emlab.query_object_parameter_values_by_object_class('MarketClearingPoints')
    print(db_emlab_marketclearingpoints)
    db_emlab_powerplantdispatchplans = db_emlab.query_object_parameter_values_by_object_class('PowerPlantDispatchPlans')
    print('Done loading Databases.')

    print('Current EMLAB Tick: ' + str(current_emlab_tick))
    print('Current COMPETES Tick: ' + str(current_competes_tick))

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
    mcp_object = next(row['object_name'] for row in db_emlab_marketclearingpoints if row['parameter_name'] == 'Market' and row['parameter_value'] == 'CO2Auction' and row['alternative'] == str(current_emlab_tick))
    mcp = next(row['parameter_value'] for row in db_emlab_marketclearingpoints if row['object_name'] == mcp_object and row['parameter_name'] == 'Price')
    print('Price found: ' + str(mcp))

    print('Staging prices...')
    db_competes.import_object_parameter_values([(object_class_name, str(current_competes_tick), i, mcp, '0') for i in parameters])

    if current_emlab_tick > 0:
        print('Current EMLAB tick ' + str(current_emlab_tick) + ' > 0 so editing Fixed O&M and CAPEX')
        capacity_market_ppdps = [row['object_name'] for row in db_emlab_powerplantdispatchplans if row['parameter_name'] == 'Market' and row['parameter_value'] == 'DutchCapacityMarket' and row['alternative'] == str(current_emlab_tick - 1)]
        capacity_market_accepted_ppdps = [row['object_name'] for row in db_emlab_powerplantdispatchplans if row['object_name'] in capacity_market_ppdps and row['parameter_name'] == 'AcceptedAmount' and row['parameter_value'] > 0]
        capacity_market_participating_plants = [row['object_parameter_value'] for row in db_emlab_powerplantdispatchplans if row['object_name'] in capacity_market_accepted_ppdps and row['parameter_name'] == 'Plant']
        capacity_market_participating_technologies = {row['parameter_value'] for row in db_emlab_powerplantdispatchplans if row['object_name'] in capacity_market_participating_plants and row['parameter_name'] == 'TECHTYPENL'}
        print('The participating technologies in the capacity market were: ' + str(capacity_market_participating_technologies))

        previous_cm_market_clearing_price = 0
        if current_emlab_tick > 1:
            previous_cm_market_clearing_point = next(row['object_name'] for row in db_emlab_marketclearingpoints if row['parameter_name'] == 'Market' and row['parameter_value'] == 'DutchCapacityMarket' and row['alternative'] == str(current_emlab_tick - 2))
            previous_cm_market_clearing_price = next(row['parameter_value'] for row in db_emlab_marketclearingpoints if row['object_name'] == previous_cm_market_clearing_point and row['parameter_name'] == 'Price')
            previous_cm_market_clearing_price = previous_cm_market_clearing_price / 1000    # EMLAB is in Euro / MWh - COMPETES is in Euro / kWh
            print('Current EMLab tick > 1, previous Capacity Market clearing price is ' + str(previous_cm_market_clearing_price))
        else:
            print('Current EMLab tick <= 1, previous CM clearing price set to 0')

        current_cm_market_clearing_point = next(row['object_name'] for row in db_emlab_marketclearingpoints if row['parameter_name'] == 'Market' and row['parameter_value'] == 'DutchCapacityMarket' and row['alternative'] == str(current_emlab_tick - 1))
        current_cm_market_clearing_price = next(row['parameter_value'] for row in db_emlab_marketclearingpoints if row['parameter_name'] == current_cm_market_clearing_point and row['parameter_name'] == 'Price')
        current_cm_market_clearing_price = current_cm_market_clearing_price / 1000      # EMLAB is in Euro / MWh - COMPETES is in Euro / kWh
        print('Current CM Market Clearing Price: ' + str(current_cm_market_clearing_price))

        for participating_technology in capacity_market_participating_technologies:
            print('Editing CAPEX and Fixed O&M for ' + str(participating_technology))
            db_overnight_cost_map = db_competes.query_object_parameter_values_by_object_class_and_object_name('Overnight Cost (OC)', participating_technology)
            db_initial_overnight_cost_map = db_competes.query_object_parameter_values_by_object_class_and_object_name('INIT Overnight Cost (OC)', participating_technology)
            db_technology_combi_map = db_competes.query_object_parameter_values_by_object_class_and_object_name('Technologies', participating_technology)
            for db_technology_map_key in db_technology_combi_map.indexes:
                db_technology_map = db_technology_combi_map.get_value(db_technology_map_key)
                fuel = ''
                fixed_om = 0
                for key in db_technology_map.indexes:
                    if key == 'FUELNEW':
                        fuel = db_technology_map.get_value(key)
                    elif key == 'FIXED O&M':
                        fixed_om = float(db_technology_map.get_value(key))
                print('Technology FUEL ' + fuel + ' and Fixed O&M ' + str(fixed_om))

                if fixed_om == 0:
                    print('Fixed O&M is 0, so backtrack CAPEX difference from previous tick')
                    print('Backtracking previous CAPEX reduction...')
                    previous_capex = db_overnight_cost_map.get_value(fuel).get_value(str(current_competes_tick - 1))
                    previous_original_capex = db_initial_overnight_cost_map.get_value(fuel).get_value(str(current_competes_tick - 1))

                    # First backtrack original value of CAPEX and Fixed O&M
                    if previous_capex + previous_cm_market_clearing_price > previous_original_capex:
                        fixed_om = previous_capex + previous_cm_market_clearing_price - previous_original_capex
                        print('Previous CAPEX ' + str(previous_capex) + ' with MCP ' + str(previous_cm_market_clearing_price) + ' exceeded original price ' + str(previous_original_capex) + ' so adjust Fixed O&M to ' + str(fixed_om))
                else:
                    print('Fixed O&M greater than 0, so add entire previous MCP')
                    fixed_om += previous_cm_market_clearing_price

                capex_map = db_overnight_cost_map.get_value(fuel)
                if capex_map is not None:
                    current_capex = capex_map.get_value(str(current_competes_tick))

                    # Now subtract
                    fixed_om -= current_cm_market_clearing_price
                    if fixed_om < 0:
                        current_capex += fixed_om   # Fixed_OM is negative
                        fixed_om = 0

                    print('New Fixed O&M: ' + str(fixed_om))
                    print('New CAPEX: ' + str(current_capex))
                    capex_map.set_value(str(current_competes_tick), float(current_capex))
                    db_overnight_cost_map.set_value(fuel, capex_map)
                    db_technology_map.set_value('FIXED O&M', float(fixed_om))
                    db_technology_combi_map.set_value(db_technology_map_key, db_technology_map)

                    db_competes.import_object_parameter_values([('Technologies', participating_technology, 'Technologies', db_technology_combi_map, '0'),
                                                                ('Overnight Cost (OC)', participating_technology, 'Overnight Cost (OC)', db_overnight_cost_map, '0')])
                else:
                    print('Fuel ' + fuel + ' not in Overnight Cost (OC) table for tech ' + participating_technology)

    print('Committing...')
    db_competes.commit('Committing EMLAB to COMPETES script. EMLab tick: ' + str(current_emlab_tick) +
                       ', COMPETES tick: ' + str(current_competes_tick))

    db_competes.close_connection()
    db_emlab.close_connection()
    print('Done!')
except Exception as e:
    print('Exception occurred: ' + str(e))
    raise
finally:
    print('Closing database connections...')
    db_emlab.close_connection()
    db_competes.close_connection()
    print('===== End of EMLab to COMPETES script =====')



