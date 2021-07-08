"""
This file contains all interactions with the system clock.
A tick is one year.

Jim Hommes - 7-4-2021
"""
import sys
from util.spinedb import SpineDB

db_url = sys.argv[1]
db = SpineDB(db_url)

object_name = 'SystemClockTicks'
object_parameter_value_name = 'ticks'

if len(sys.argv) >= 2:
    if sys.argv[2] == 'initialize_clock':
        print('Initializing clock (tick 0)')
        db.import_object_classes([object_name])
        db.import_objects([(object_name, object_name)])
        db.import_data({'object_parameters': [[object_name, object_parameter_value_name]]})
        db.import_alternatives([str(0)])
        db.import_object_parameter_values([(object_name, object_name, object_parameter_value_name, 0, '0')])
        db.commit('Clock intialization')
        print('Done initializing clock (tick 0)')

    if sys.argv[2] == 'increment_clock':
        print('Incrementing Clock (tick +1)')
        db_data = db.export_data()

        step = 10

        new_tick = step + max([int(i[3]) for i in db_data['object_parameter_values'] if i[0] == i[1] == object_name
                               and i[2] == object_parameter_value_name])
        db.import_alternatives([str(new_tick)])
        db.import_object_parameter_values([(object_name, object_name, object_parameter_value_name, new_tick,
                                            str(new_tick))])
        db.commit('Clock increment')
        print('Done incrementing clock (tick +1)')
else:
    print('No mode specified.')
