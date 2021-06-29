"""
This script prepares the COMPETES output files for import by Spine Toolbox.
This means that the most recent output file from COMPETES/Results will be copied to a output file without year,
as defined in Spine Toolbox.

Jim Hommes - 21-6-2021
"""
import sys
from shutil import copyfile
from spinedb import SpineDB
from helper_functions import get_current_ticks

print('===== Starting COMPETES Output Preparation script =====')
print('Loading Databases...')
db_emlab = SpineDB(sys.argv[1])

try:
    current_emlab_tick, current_competes_tick, current_competes_tick_rounded = get_current_ticks(db_emlab, 2020)
    print('Current EMLAB Tick: ' + str(current_emlab_tick))
    print('Current COMPETES Tick: ' + str(current_competes_tick))

    print('Copying files...')
    copyfile('../../COMPETES/Results/Output_Dynamic_Gen&Trans_?.xlsx'.replace('?', str(current_competes_tick)),
             '../../COMPETES/Results/current_Gen&Trans.xlsx')

    print('Done')
except Exception as e:
    print('Exception occurred: ' + str(e))
finally:
    print('Closing database connection...')
    db_emlab.close_connection()
    print('===== End of COMPETES Output Preparation script =====')