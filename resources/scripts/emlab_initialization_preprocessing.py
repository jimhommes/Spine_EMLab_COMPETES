"""
Because of the interpretation of Spine data, the EMLAB SpineDB needs preprocessing.
This script is an initialization preprocessing: it should be executed ONLY ONCE when executing the imports
for a fresh run.
This script replaces capitalized fuelnames which is an inconsistency in COMPETES. It requires COMPETES's FuelMap to
map the correct fuelnames.
This script also imports the VRE for NL in EM-Lab. This is because there is no conditional processing in SpineDB:
it can not filter the NED element from the VRE Capacities sheet. This is why it imports this from COMPETES SpineDB.


Arg1: URL to SpineDB EM-Lab
Arg2: URL to SpineDB COMPETES

Jim Hommes - 29-6-2021
"""
from spinedb import SpineDB
import sys


def replace_power_generating_technology_fuel_names(db_emlab, db_emlab_fuelmap, db_emlab_technologies):
    """
    This function replaces the full caps Fuel names which are found in the init files. The text used is lowercase and
    can be found in the FuelMap. This function replaces the fuelnames (if first tick, so it only happens once).
    Then it's according to the other references.

    :param db_emlab: SpineDB
    :param db_emlab_fuelmap: FuelMap as queried in EMLAB SpineDB
    :param current_emlab_tick: int
    :param db_emlab_technologies: Technologies as queried in EMLAB SPineDB
    """
    print('Setting correct PowerGeneratingTechnologyFuel names...')
    for row in db_emlab_technologies:
        if row['parameter_name'] == 'FUELTYPENEW':
            old_substance_name = next(i['parameter_value'] for i in db_emlab_technologies if
                                      i['object_name'] == row['object_name'] and i['parameter_name'] == 'FUELNEW')
            try:
                new_substance_name = next(fm_row['parameter_value'] for fm_row in db_emlab_fuelmap if
                                          fm_row['object_name'] == row['parameter_value']).get_value(
                    old_substance_name)
                db_emlab.import_object_parameter_values(
                    [('PowerGeneratingTechnologyFuel', row['object_name'], 'FUELNEW', new_substance_name, '0')])
            except StopIteration:  # Not all technologies are in the FuelMap
                print('Tech not found in FuelMap: ' + row['parameter_value'])
    print('Done setting correct PowerGeneratingTechnologyFuel names')


def import_initial_vre(db_emlab, db_competes_vre_capacities, initialization_year):
    """
    This function plucks the VRE in NED of this year and imports the MW into SpineDB EM Lab.

    :param db_emlab: SpineDB
    :param db_competes_vre_capacities: VRE Capacity table from COMPETES
    :param initialization_year: The year for which the MW to get
    """
    for row in db_competes_vre_capacities:
        amount_mw = row['parameter_value'].get_value(str(initialization_year)).get_value('NED')\
            .get_value('Initial Capacity(MW)')
        db_emlab.import_object_parameter_values([('PowerPlants', row['object_name'], 'MWNL', amount_mw, '0')])


def execute_all_initialization_preprocessing():
    """
    This function executes all steps of this script.
    """
    print('Creating connection to SpineDB...')
    db_emlab = SpineDB(sys.argv[1])
    db_competes = SpineDB(sys.argv[2])
    print('Querying SpineDB...')
    db_emlab_fuelmap = db_emlab.query_object_parameter_values_by_object_class('FuelMap')
    db_emlab_technologies = db_emlab.query_object_parameter_values_by_object_class('PowerGeneratingTechnologyFuel')
    db_competes_vre_capacities = db_competes.query_object_parameter_values_by_object_class('VRE Capacities')
    print('Done querying')

    try:
        replace_power_generating_technology_fuel_names(db_emlab, db_emlab_fuelmap, db_emlab_technologies)
        import_initial_vre(db_emlab, db_competes_vre_capacities, 2020)

        print('Committing...')
        db_emlab.commit('DB EMLAB Initialization Preprocessing')

    except Exception as e:
        print('Exception thrown: ' + str(e))
        raise
    finally:
        db_emlab.close_connection()


print('===== Start EMLAB Preprocessing script =====')
execute_all_initialization_preprocessing()
print('===== End of EMLAB Preprocessing script =====')