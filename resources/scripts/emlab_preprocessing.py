"""
Because of the interpretation of Spine data, the EMLAB SpineDB needs preprocessing.
This script sets all the power plant statuses to OPR or DECOM according to EMLAB rules and not the COMPETES rules.
This is necessary as COMPETES works with aggregates: EMLAB with statuses actual to the current tick.

Jim Hommes - 29-6-2021
"""
import sys
from spinedb import *
from helper_functions import get_current_ticks


print('===== Start EMLAB Preprocessing script =====')
print('Creating connection to SpineDB...')
db_emlab = SpineDB(sys.argv[1])
print('Querying SpineDB...')
db_emlab_powerplants = db_emlab.query_object_parameter_values_by_object_class('PowerPlants')
current_emlab_tick, current_competes_tick, current_competes_tick_rounded = get_current_ticks(db_emlab, 2020)
print('Done querying')

print('Current EMLAB Tick: ' + str(current_emlab_tick))
print('Current COMPETES Tick: ' + str(current_competes_tick))

powerplant_statuses = {row['object_name']: row['parameter_value'] for row in db_emlab_powerplants if row['object_class_name'] == 'PowerPlants' and row['parameter_name'] == 'STATUSNL'}
print(powerplant_statuses)

# Check if build year >= current_competes_tick
for row in [i for i in db_emlab_powerplants if i['object_class_name'] == 'PowerPlants' and i['parameter_name'] == 'ON-STREAMNL']:
    if row['parameter_value'] <= current_competes_tick:
        powerplant_statuses[row['object_name']] = 'OPR'
    else:
        powerplant_statuses[row['object_name']] = 'DECOM'

# If name has a (D), set referred to unit to DECOM
for row in [i for i in db_emlab_powerplants if i['object_class_name'] == 'PowerPlants' and i['parameter_name'] == 'ON-STREAMNL']:
    if '(D)' in row['object_name']:
        powerplant_statuses[row['object_name']] = 'DECOM'
        if row['parameter_value'] <= current_competes_tick:
            powerplant_statuses[row['object_name'].replace('(D)', '')] = 'DECOM'

# Sum all BIOMASS, WASTE and HYDRO
# Set them all DECOM and introduce one new OPR with the sum
powerplants_biomass = {row['object_name']: row['parameter_value'] for row in db_emlab_powerplants if row['object_class_name'] == 'PowerPlants' and 'BIOMASS Standalone' in row['object_name'] and row['parameter_name'] == 'ON-STREAMNL'}
powerplants_hydro = {row['object_name']: row['parameter_value'] for row in db_emlab_powerplants if row['object_class_name'] == 'PowerPlants' and 'HYDRO CONV' in row['object_name'] and row['parameter_name'] == 'ON-STREAMNL'}
powerplants_waste = {row['object_name']: row['parameter_value'] for row in db_emlab_powerplants if row['object_class_name'] == 'PowerPlants' and 'WASTE Standalone' in row['object_name'] and row['parameter_name'] == 'ON-STREAMNL'}

mw_biomass_sum = 0
for (plant, year) in powerplants_biomass.items():
    if 'SUM' not in plant:
        powerplant_statuses[plant] = 'DECOM'
        if year <= current_competes_tick:
            mw_biomass_sum += next(row['parameter_value'] for row in db_emlab_powerplants if row['object_class_name'] == 'PowerPlants' and row['object_name'] == plant and row['parameter_name'] == 'MWNL')

mw_hydro_sum = 0
for (plant, year) in powerplants_hydro.items():
    if 'SUM' not in plant:
        powerplant_statuses[plant] = 'DECOM'
        if year <= current_competes_tick:
            mw_hydro_sum += next(row['parameter_value'] for row in db_emlab_powerplants if row['object_class_name'] == 'PowerPlants' and row['object_name'] == plant and row['parameter_name'] == 'MWNL')

mw_waste_sum = 0
for (plant, year) in powerplants_waste.items():
    if 'SUM' not in plant:
        powerplant_statuses[plant] = 'DECOM'
        if year <= current_competes_tick:
            mw_waste_sum += next(row['parameter_value'] for row in db_emlab_powerplants if row['object_class_name'] == 'PowerPlants' and row['object_name'] == plant and row['parameter_name'] == 'MWNL')

print('End:')
print(powerplant_statuses)

print('Setting up for DB import...')
db_emlab.import_object_parameter_values([('PowerPlants', 'NED BIOMASS Standalone SUM', 'MWNL', mw_biomass_sum, '0'),
                                         ('PowerPlants', 'NED HYDRO CONV SUM', 'MWNL', mw_hydro_sum, '0'),
                                         ('PowerPlants', 'NED WASTE Standalone SUM', 'MWNL', mw_waste_sum, '0')])

object_parameter_values = [('PowerPlants', object_name.strip(), 'STATUSNL', value, '0') for (object_name, value) in powerplant_statuses.items()]
db_emlab.import_object_parameter_values(object_parameter_values)
db_emlab.commit('DB EMLAB Preprocessing tick ' + str(current_competes_tick))

print('===== End of EMLAB Preprocessing script =====')