"""
This script handles all preparations necessary for the execution of COMPETES.
This entails translating the COMPETES SpineDB to MS Access databases.

Jim Hommes - 1-6-2021
"""
import pyodbc
import shutil
import sys
from spinedb import SpineDB


def export_to_mdb(path: str, filename: str, type1: dict):
    print('Initializing connection to ' + filename)
    try:
        con_string = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + path + filename + ';'
        conn = pyodbc.connect(con_string)
        cursor = conn.cursor()
        print("Connected To " + filename)

        print('Staging Type 1 Mappings...')
        for table in type1.keys():
            export_type1(cursor, table, type1[table])

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
            if type(param_value) is str:
                param_values.append(param_value)
            else:
                param_values.append(str(param_value))
        sql_statement = 'INSERT INTO [' + table_name + '] (['+id_param+'], ' + ', '.join(['[' + str(i) + ']' for i in param_names]) + \
                        ") VALUES (?, " + ', '.join(['?' for i in param_values]) + ');'
        values = (unique_param,) + tuple(param_values)
        print(values)
        print(sql_statement.replace('?', '%s') % values)
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

export_to_mdb(r'E:\Dropbox\workspace\Spine_EMLab_COMPETES\COMPETES\Data\\', 'COMPETES EU 2050-KIP.mdb',
              {'BusCountry': 'Bus',
               'Country': 'Country',
               'FuelGen': 'FUELGEN',
               'FuelType': 'FUELNEW',
               'Input_Years': 'Input Year',
               'Months': 'MonthDef',
               'Season': 'SeasonInput',
               'Techtype': 'FUELTYPENEW',
               'VRE Technologies': 'Technology'})

type1pp = {'Installed Capacity Abroad': '',
           'Installed Capacity-RES Abroad': '',
           'NL Installed Capacity (+heat)': '',
           'NL Installed Capacity-RES (+he': ''}

print('===== End of COMPETES SpineDB to MS Access script =====')




