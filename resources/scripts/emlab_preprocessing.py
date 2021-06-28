import sys
from spinedb import *

print('===== Start EMLAB Preprocessing script =====')
print('Creating connection to SpineDB...')
db_emlab = SpineDB(sys.argv[1])
print('Exporting SpineDB...')
db_emlab_data = db_emlab.export_data()
print('Done exporting')

print('Loading current EM-Lab tick...')
current_emlab_tick = max(
    [int(i[3]) for i in db_emlab_data['object_parameter_values'] if i[0] == i[1] == 'SystemClockTicks' and
     i[2] == 'ticks'])
current_competes_tick = current_emlab_tick + 2020
current_competes_tick_rounded = 2020 + round(current_emlab_tick / 5) * 5
print('Current EM-Lab tick is ' + str(current_emlab_tick) +
      ', which translates to COMPETES tick ' + str(current_competes_tick))

powerplant_statuses = {object_name: parameter_value for (object_class, object_name, parameter_name, parameter_value, alternative) in db_emlab_data['object_parameter_values'] if object_class == 'PowerPlants' and parameter_name == 'STATUSNL'}
print(powerplant_statuses)
# Check if build year >= current_competes_tick
for (object_class, object_name, parameter_name, parameter_value, alternative) in [i for i in db_emlab_data['object_parameter_values'] if i[0] == 'PowerPlants' and i[2] == 'ON-STREAMNL']:
    if parameter_value <= current_competes_tick:
        powerplant_statuses[object_name] = 'OPR'
    else:
        powerplant_statuses[object_name] = 'DECOM'

# If name has a (D), set referred to unit to DECOM
for (object_class, object_name, parameter_name, parameter_value, alternative) in [i for i in db_emlab_data['object_parameter_values'] if i[0] == 'PowerPlants' and i[2] == 'ON-STREAMNL']:
    if '(D)' in object_name:
        powerplant_statuses[object_name] = 'DECOM'
        if parameter_value <= current_competes_tick:
            powerplant_statuses[object_name.replace('(D)', '')] = 'DECOM'

# Sum all BIOMASS, WASTE and HYDRO
# Set them all DECOM and introduce one new OPR with the sum
powerplants_biomass = {object_name: parameter_value for (object_class, object_name, parameter_name, parameter_value, alternative) in db_emlab_data['object_parameter_values'] if object_class == 'PowerPlants' and 'BIOMASS Standalone' in object_name and parameter_name == 'ON-STREAMNL'}
powerplants_hydro = {object_name: parameter_value for (object_class, object_name, parameter_name, parameter_value, alternative) in db_emlab_data['object_parameter_values'] if object_class == 'PowerPlants' and 'HYDRO CONV' in object_name and parameter_name == 'ON-STREAMNL'}
powerplants_waste = {object_name: parameter_value for (object_class, object_name, parameter_name, parameter_value, alternative) in db_emlab_data['object_parameter_values'] if object_class == 'PowerPlants' and 'WASTE Standalone' in object_name and parameter_name == 'ON-STREAMNL'}

mw_biomass_sum = 0
for (plant, year) in powerplants_biomass.items():
    if 'SUM' not in plant:
        powerplant_statuses[plant] = 'DECOM'
        if year <= current_competes_tick:
            mw_biomass_sum += next(i[3] for i in db_emlab_data['object_parameter_values'] if i[0] == 'PowerPlants' and i[1] == plant and i[2] == 'MWNL')

mw_hydro_sum = 0
for (plant, year) in powerplants_hydro.items():
    if 'SUM' not in plant:
        powerplant_statuses[plant] = 'DECOM'
        if year <= current_competes_tick:
            mw_hydro_sum += next(i[3] for i in db_emlab_data['object_parameter_values'] if i[0] == 'PowerPlants' and i[1] == plant and i[2] == 'MWNL')

mw_waste_sum = 0
for (plant, year) in powerplants_waste.items():
    if 'SUM' not in plant:
        powerplant_statuses[plant] = 'DECOM'
        if year <= current_competes_tick:
            mw_waste_sum += next(i[3] for i in db_emlab_data['object_parameter_values'] if i[0] == 'PowerPlants' and i[1] == plant and i[2] == 'MWNL')

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