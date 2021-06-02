"""
This script handles all preparations necessary for the execution of COMPETES.
This entails translating the COMPETES SpineDB to MS Access databases.

Jim Hommes - 1-6-2021
"""
import pyodbc
import shutil
import sys
from spinedb import SpineDB


def export_to_mdb(path: str, filename: str, type1: dict, type2: dict):
    print('Initializing connection to ' + filename)
    try:
        con_string = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + path + filename + ';'
        conn = pyodbc.connect(con_string)
        cursor = conn.cursor()
        print("Connected To " + filename)

        print('Staging Type 1 Mappings...')
        for table in type1.keys():
            print('Exporting table ' + table)
            export_type1(cursor, table, type1[table])
        print('Finished Type 1 Mappings')

        print('Staging Type 2 Mappings...')
        for (table, (obj_param_name, index_param_name)) in type2.items():
            print('Exporting table ' + table)
            export_type2(cursor, table, obj_param_name, index_param_name)
        print('Finished Type 2 Mappings')

        print('Committing...')
        cursor.commit()
        cursor.close()
        conn.close()
        print('Done')

    except pyodbc.Error as e:
        print("Error in Connection", e)


def export_type1(cursor, table_name, id_param):
    for (_, unique_param, _) in [i for i in db_competes_data['objects'] if i[0] == table_name]:
        param_names = []
        param_values = []
        for (_, _, param_name, param_value, _) in [i for i in db_competes_data['object_parameter_values']
                                                   if i[0] == table_name and i[1] == unique_param]:
            param_names.append(param_name)
            param_values.append(str(param_value))

        sql_statement = 'INSERT INTO [' + table_name + '] (['+id_param+'], ' + ', '.join(['[' + str(i) + ']' for i in param_names]) + \
                        ") VALUES (?, " + ', '.join(['?' for i in param_values]) + ');'
        values = (unique_param,) + tuple(param_values)
        # print(values)
        # print(sql_statement.replace('?', '%s') % values)
        cursor.execute(sql_statement, values)


def export_type2(cursor, table_name, id_param, index_param):
    for (_, unique_param, _) in [i for i in db_competes_data['objects'] if i[0] == table_name]:
        value_map = next(i[3] for i in db_competes_data['object_parameter_values'] if i[0] == table_name and i[1] == unique_param)
        for value_map_row in value_map.to_dict()['data']:
            index = value_map_row[0]
            param_values = [('[' + str(i[0]) + ']', i[1]) for i in value_map_row[1]['data']]
            sql_statement = 'INSERT INTO [' + table_name + '] ([' + id_param + '],[' + index_param + '],' + ','.join([i[0] for i in param_values]) + ') VALUES (?,?,' + ','.join(['?' for i in param_values]) + ');'
            values = (unique_param, index,) + tuple(i[1] for i in param_values)
            # print(values)
            # print(sql_statement.replace('?', '%s') % values)
            cursor.execute(sql_statement, values)



print('===== Starting COMPETES SpineDB to MS Access script =====')

print('Copying empty databases...')
originalfiles = sys.argv[2:]
targetfiles = [i.replace('empty_', '') for i in originalfiles]

for originalfile in originalfiles:
    shutil.copyfile(originalfile, originalfile.replace("empty_", ""))
print('Done copying empty databases')

print('Connecting and exporting SpineDB...')
db_competes = SpineDB(sys.argv[1])
db_competes_data = db_competes.export_data()
db_competes.close_connection()
print('Done')

path_to_data = originalfiles[0].split("empty_")[0]
export_to_mdb(path_to_data, 'COMPETES EU 2050-KIP.mdb',
              {'BusCountry': 'Bus',
               'Country': 'Country',
               'FuelGen': 'FUELGEN',
               'FuelType': 'FUELNEW',
               'Input_Years': 'Input Year',
               'Months': 'MonthDef',
               'Season': 'SeasonInput',
               'Techtype': 'FUELTYPENEW',
               'VRE Technologies': 'Technology'},
              {'Coal Tax NL': ('Country', 'Year'),
               'DR EV': ('Bus', 'Year'),
               'DR H2': ('Bus', 'Year'),
               'DR Heat': ('Bus', 'Year'),
               'DR Shifting': ('Bus', 'Year'),
               'Days': ('DayOrder', 'DayInput'),
               'Demand Response': ('DR', 'Year'),
               'Economic Lifetime': ('FUELTYPENEW', 'FuelNew'),
               'FuelMap': ('FUELTYPE', 'FUEL1'),
               'H2 System': ('Bus', 'Technology'),
               'H2 Technologies': ('Technology', 'Year'),
               'Historic Nuclear Availability': ('Month', 'Year'),
               'Hourly DR Profiles': ('Demand Year', 'Time'),
               'Hourly Demand': ('Demand Year', 'Time'),
               'Hourly EV Profiles': ('Demand Year', 'Time'),
               'Hourly H2 Demand': ('Demand Year', 'Time'),
               'Hourly Mustrun Hydro': ('Run Year', 'Time'),
               'Incidence matrix': ('Bus', 'Line'),
               'New Technologies': ('FUELTYPENEW', 'InvCountry'),
               'Overnichgt Cost (OC)': ('FUELTYPENEW', 'FUELNEW'),
               'SeasonDayHourCombo': ('Season1', 'Time'),
               'SeasonTime': ('Season1', 'Time'),
               'Technologies': ('FUELTYPENEW', 'TechnOrder'),
               'Unit Commitment Database': ('FUELTYPE', 'FUEL'),
               'VRE Capacities': ('Technology', 'Bus'),
               'VRE LoadFactors': ('Technology', 'VRE Year')})

type1pp = {'Installed Capacity Abroad': '',
           'Installed Capacity-RES Abroad': '',
           'NL Installed Capacity (+heat)': '',
           'NL Installed Capacity-RES (+he': ''}

type2pp = {'H2 Storage': ('', ''),
           'Storage': ('', '')}

print('===== End of COMPETES SpineDB to MS Access script =====')




