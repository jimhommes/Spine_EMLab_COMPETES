"""
This script handles all preparations necessary for the execution of COMPETES.
This entails translating the COMPETES SpineDB to MS Access databases.

Jim Hommes - 1-6-2021
"""
import pyodbc
import shutil
import sys
from spinedb import SpineDB

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
print('Done')

print('Initializing connection to COMPETES EU 2050-KIP.mdb')
try:
    con_string = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=E:\Dropbox\workspace\Spine_EMLab_COMPETES\COMPETES\Data\COMPETES EU 2050-KIP.mdb;'
    conn = pyodbc.connect(con_string)
    cursor = conn.cursor()
    print("Connected To Database")

    id_param_names = {'BusCountry': 'Bus'}

    print('Adding some values...')
    for (table_name, unique_param, _) in [i for i in db_competes_data['objects'] if i[0]=='BusCountry']:
        param_names = []
        param_values = []
        for (_, _, param_name, param_value, _) in [i for i in db_competes_data['object_parameter_values']
                                                   if i[0] == table_name and i[1] == unique_param]:
            param_names.append(param_name)
            if type(param_value) is str:
                param_values.append("'" + param_value + "'")
            else:
                param_values.append(str(param_value))
        sql_statement = 'INSERT INTO BusCountry (' + id_param_names['BusCountry'] + ', ' + ', '.join([str(i) for i in param_names]) + ") VALUES ('" + unique_param + "', " + ', '.join(param_values) + ');'
        print(sql_statement)
        cursor.execute(sql_statement)
    cursor.commit()
    cursor.close()
    conn.close()

except pyodbc.Error as e:
    print("Error in Connection", e)

print('===== End of COMPETES SpineDB to MS Access script =====')