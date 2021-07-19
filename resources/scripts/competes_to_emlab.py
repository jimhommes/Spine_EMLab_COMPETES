"""
This script handles all communication passed from the COMPETES Excel output to the EM-Lab SpineDB.
It handles the MarketClearingPoint from the Hourly Nodal Prices and the unit generation as PowerPlantDispatchPlans.
It also implements the investment and decommissioning decisions into EMLAB and COMPETES.

Arg1: URL of EMLAB SpineDB
Arg2: URL of COMPETES SpineDB
Arg3: Relative path to COMPETES Results folder
Arg4: Filename of COMPETES output Gen&Trans with a "?" as placeholder for the year
Arg5: Filename of COMPETES output UC with a "?" as placeholder for the year

Jim Hommes - 10-6-2021
"""
import sys
import pandas
import numpy as np
from datetime import datetime
from spinedb import SpineDB
from helper_functions import get_current_ticks


def query_databases(db_emlab, db_competes):
    """
    This function queries the databases and retrieves all necessary data.

    :param db_emlab: SpineDB Object of EM-Lab
    :param db_competes: SpineDB Object of COMPETES
    :return: the queried data
    """
    print('Querying databases...')
    db_emlab_powerplants = db_emlab.query_object_parameter_values_by_object_class('PowerPlants')
    db_emlab_ppdps = db_emlab.query_object_parameter_values_by_object_class('PowerPlantDispatchPlans')
    db_competes_powerplants = db_competes.query_object_parameter_values_by_object_classes(
        ['Installed Capacity Abroad', 'Installed Capacity-RES Abroad', 'NL Installed Capacity (+heat)',
         'NL Installed Capacity-RES (+he'])
    db_emlab_mcps = db_emlab.query_object_parameter_values_by_object_class('MarketClearingPoints')
    print('Done')
    return db_emlab_powerplants, db_emlab_ppdps, db_competes_powerplants, db_emlab_mcps


def read_excel_sheets(path_to_competes_results, file_name_gentransinv, file_name_gentransdisp):
    """
    This function reads all Excel sheets output by COMPETES. This is done with pandas.

    :param path_to_competes_results: URL
    :param file_name_gentransinv: Filename of the Investment output
    :param file_name_uc: Filename of the Unit Commitment output
    :return: The pandas dataframes of the read Excel sheets
    """
    # Unit Commitment
    hourly_nodal_prices_df = pandas.read_excel(path_to_competes_results + '/' + file_name_gentransdisp,
                                               'Hourly Nodal Prices')
    unit_generation_df = pandas.read_excel(path_to_competes_results + '/' + file_name_gentransdisp,
                                           'NL Unit Generation', index_col=0, skiprows=1)
    hourly_nl_balance_df = pandas.read_excel(path_to_competes_results + '/' + file_name_gentransdisp,
                                             'Hourly NL Balance', skiprows=1)

    # Investment and Decom decisions
    new_generation_capacity_df = pandas.read_excel(path_to_competes_results + '/' + file_name_gentransinv,
                                                   'New Generation Capacity', skiprows=2, usecols='A:D,G:X')
    decommissioning_df = pandas.read_excel(path_to_competes_results + '/' + file_name_gentransinv, 'Decommissioning',
                                           skiprows=2, usecols='A:C')
    vre_investment_df = pandas.read_excel(path_to_competes_results + '/' + file_name_gentransinv, 'VRE investment',
                                          skiprows=2, usecols='A:D')

    return hourly_nodal_prices_df, unit_generation_df, new_generation_capacity_df, decommissioning_df, \
           vre_investment_df, hourly_nl_balance_df


def prepare_competes_importer(vre_investment_df, current_competes_tick, path_to_competes_results):
    """
    This file creates the Excel sheet which is imported by the Importer block in Spine.
    It contains the VRE investments. This way the importer handles all mappings.

    :param vre_investment_df: Loaded from the Excel sheets
    :param current_competes_tick: int
    :param path_to_competes_results: URL
    """
    print('Prepare Excel file for COMPETES Importer')
    # Bus	Initial Capacity(MW)	New Capacity(MW)	Potential(MW)	Year	Technology	If Investment	Firm
    datalength = len(vre_investment_df['Potential'].values.tolist())
    data_csv = {'Bus': vre_investment_df['Bus'].values.tolist(),
                'Initial Capacity(MW)': vre_investment_df['Initial'].values.tolist(),
                'New Capacity(MW)': [''] * datalength,
                'Potential(MW)': vre_investment_df['Potential'].values.tolist(),
                'Year': [str(current_competes_tick)] * datalength,
                'Technology': vre_investment_df['WindOn'].values.tolist(),
                'If Investment': [''] * datalength,
                'Firm': [''] * datalength}
    pandas.DataFrame(data_csv).to_excel(path_to_competes_results + '/COMPETES_Output_for_import.xlsx', index=False)
    print('Done')


def export_decommissioning_decisions_to_emlab_and_competes(db_competes, db_emlab, db_competes_powerplants,
                                                           decommissioning_df, current_competes_tick,
                                                           current_emlab_tick, step):
    """
    This function exports all decommissioning decisions to EMLab and COMPETES.
    This means that the duplicate objects (the ones with (D) in the title) will be changed in their year, or
    ON-STREAMNL. This will be set to the current year.
    The preprocessing EMLab block will make implement the STATUSNL afterwards.

    :param db_competes: SpineDB
    :param db_emlab: SpineDB
    :param db_competes_powerplants: The queried results of the COMPETES powerplants
    :param decommissioning_df: The Decommissioning values from the COMPETES output
    :param current_competes_tick: int
    :param current_emlab_tick: int
    """
    print('Exporting Decommissioning to EMLAB and COMPETES...')
    for index, row in decommissioning_df.iterrows():
        try:
            power_plant_name_decom_version_row = next(
                i for i in db_competes_powerplants if row['unit'] in i['object_name'] and '(D)' in i['object_name'])
            power_plant_name_decom_version = power_plant_name_decom_version_row['object_name']
            db_competes.import_object_parameter_values([(power_plant_name_decom_version_row['object_class_name'],
                                                         power_plant_name_decom_version, 'ON-STREAMNL',
                                                         current_competes_tick, '0')])
            if row['node'] == 'NED':
                # If node is NED, export to EMLAB
                db_emlab.import_object_parameter_values([('PowerPlants', power_plant_name_decom_version, 'ON-STREAMNL',
                                                          current_competes_tick, str(current_emlab_tick + step))])
        except StopIteration:
            print('No DECOM version found for plant ' + row['unit'])
    print('Done')


def export_vre_investment_decisions_to_emlab(db_emlab, current_emlab_tick, vre_investment_df,
                                             db_emlab_powerplants, step):
    """
    This function exports all VRE Investment decisions. For COMPETES the Importer block in Spine is used.
    See function prepare_competes_importer.

    :param db_emlab: SpineDB
    :param current_emlab_tick: int
    :param vre_investment_df: Dataframe of VRE Investment decisions from COMPETES output
    :param db_emlab_powerplants: Queried Powerplants from EMLab
    """
    print('Exporting VRE Investment Decisions to EMLAB...')
    print('Export to EMLAB')
    for index, vre_row in vre_investment_df.iterrows():
        try:
            old_mw = next(row['parameter_value'] for row in db_emlab_powerplants if
                          row['object_name'] == vre_row['WindOn'] and row['parameter_name'] == 'MWNL')
            db_emlab.import_object_parameter_values([('PowerPlants', vre_row['WindOn'], 'MWNL',
                                                  float(old_mw) + float(vre_row['Initial']),
                                                  str(current_emlab_tick + step))])
        except KeyError:
            print('No VRE Investments found')
            break
    print('Done')
    print('Done exporting VRE Investment Decisions to EMLAB')


def export_investment_decisions_to_emlab_and_competes(db_emlab, db_competes, current_emlab_tick,
                                                      new_generation_capacity_df, current_competes_tick, step):
    """
    This function exports all Investment decisions.

    :param db_emlab: SpineDB
    :param db_competes: SpineDB
    :param new_generation_capacity_df: Dataframe of new generation capacity from COMPETES output
    """
    print('Exporting Investment Decisions to EMLAB and COMPETES...')
    for index, row in new_generation_capacity_df.iterrows():
        print('Export to COMPETES')
        param_values = [i for i in row[4:].items() if i[0] != 'UNITEU']
        param_values = [(i[0], 0) if pandas.isnull(i[1]) else i for i in param_values]
        plant_name = row['UNITEU']
        print('New plant ' + plant_name + ' with parameters ' + str(param_values))
        db_competes.import_objects([('Installed Capacity Abroad', plant_name)])
        db_competes.import_object_parameter_values(
            [('Installed Capacity Abroad', row['UNITEU'], param_name, param_value, '0') for (param_name, param_value) in
             param_values])
        print('Done')

        print('If NED export to EMLAB')
        if row['Node'] == 'NED' and float(row['MWEU']) > 0:
            db_emlab.import_objects([('PowerPlants', plant_name)])
            param_values = [(col.replace("TECHTYPEU", "TECHTYPENL").replace("EU", "NL"), value)
                            for (col, value) in param_values if not (col == 'STATUSEU' or col == 'ON-STREAMEU')]
            param_values.insert(0, ('STATUSNL', 'DECOM'))  # Always Decom, in EMLAB_Preprocessing it will be set correctly
            param_values.insert(0, ('ON-STREAMNL', current_competes_tick))     # Year in the sheet is random and wrong
            print(param_values)
            db_emlab.import_object_parameter_values(
                [('PowerPlants', plant_name, param_index, param_value, str(current_emlab_tick + step))
                 for (param_index, param_value) in param_values])
        print('Done')
    print('Done exporting Investment Decisions to EMLAB and COMPETES')


def export_power_plant_dispatch_plans_to_emlab(db_emlab, current_emlab_tick, unit_generation_df, db_emlab_ppdps,
                                               hourly_nodal_prices_nl, db_emlab_powerplants):
    """
    This function exports all dispatch and nodal prices from COMPETES output. EMLab interprets this as
    PowerPlantDispatchPlans. In order to achieve the right results, the price of the ppdp is set at the average of
    all the prices the plant operates. Capacity is set to total capacity of the year (sum).

    :param db_emlab: SpineDB
    :param current_emlab_tick: int
    :param unit_generation_df: Dataframe of COMPETES output
    :param db_emlab_ppdps: Queried PowerPlantDispatchPlans from EMLab
    :param hourly_nodal_prices_nl: Hourly nodal prices from COMPETES
    :param db_emlab_powerplants: Queried Powerplants from EMLab
    """
    print('Exporting PowerPlantDispatchPlans into EMLAB')
    ppdp_objects_to_import = []
    ppdp_values_to_import = []
    for power_plant in unit_generation_df.columns:
        print('Staging PPDP for ' + str(power_plant))
        try:
            ppdp_name = next(i['object_name'] for i in db_emlab_ppdps if
                             i['parameter_name'] == 'Plant' and i['parameter_value'] == power_plant and i[
                                 'alternative'] == str(current_emlab_tick))
        except StopIteration:
            ppdp_name = 'PowerPlantDispatchPlan ' + str(datetime.now())
            ppdp_objects_to_import.append(('PowerPlantDispatchPlans', ppdp_name))

        accepted = sum(unit_generation_df[power_plant].values)
        if accepted > 0:
            hourly_nodal_prices_nl_where_plant_generated = [i for i in zip(unit_generation_df[power_plant].values,
                                                                           hourly_nodal_prices_nl) if i[0] > 0]
            ppdp_price = sum([float(i[0]) * float(i[1]) for i in
                              hourly_nodal_prices_nl_where_plant_generated]) / accepted if accepted > 0 else 0
            owner = next(row['parameter_value'] for row in db_emlab_powerplants if
                         row['object_name'] == power_plant and row['parameter_name'] == 'FirmNL')
            status = 'Accepted' if accepted > 0 else 'Failed'
            values = [('AcceptedAmount', accepted), ('Capacity', accepted), ('EnergyProducer', owner),
                      ('Market', 'DutchElectricitySpotMarket'), ('Plant', power_plant), ('Status', status),
                      ('Price', ppdp_price)]
            ppdp_values_to_import = ppdp_values_to_import + [
                ('PowerPlantDispatchPlans', ppdp_name, i[0], i[1], str(current_emlab_tick)) for i in values]
        else:
            print('Accepted amount == 0, not importing')
    db_emlab.import_objects(ppdp_objects_to_import)
    db_emlab.import_object_parameter_values(ppdp_values_to_import)
    print('Done exporting PowerPlantDispatchPlans to EMLAB')


def get_hourly_nodal_prices(hourly_nodal_prices_df):
    """
    This function retrieves the desired data of the dataframe of hourly nodal prices from COMPETES.

    :param hourly_nodal_prices_df:
    :return: Specific values of the Netherlands
    """
    hourly_nodal_prices_df.columns = hourly_nodal_prices_df.iloc[0]
    hourly_nodal_prices_df.drop([0])
    return hourly_nodal_prices_df['NED'][1:].values


def export_market_clearing_points_to_emlab(db_emlab, current_emlab_tick, hourly_nodal_prices_nl, db_emlab_mcps):
    """
    This function exports the MCP of the Electricity Spot Market to EM-Lab. This is the average price of all the hours.

    :param db_emlab_mcps: MCPs as queried of SpineDB EMLab
    :param db_emlab: SpineDB
    :param current_emlab_tick: int
    :param hourly_nodal_prices_nl: Hourly Nodal prices object from get_hourly_nodal_prices
    """
    print('Exporting MarketClearingPoint to EMLAB')
    hourly_nodal_prices_nl_avg = sum(hourly_nodal_prices_nl) / len(hourly_nodal_prices_nl)
    print('Average hourly nodal prices: ' + str(hourly_nodal_prices_nl_avg))

    print('Checking if MCP already exists for this run')
    try:
        newobject_mcp_name = next(i['object_name'] for i in db_emlab_mcps
                                  if i['parameter_name'] == 'Market'
                                  and i['parameter_value'] == 'DutchElectricitySpotMarket')
    except StopIteration:
        newobject_mcp_name = 'MarketClearingPoint ' + str(datetime.now())

    print('Staging...')
    values = [('Market', 'DutchElectricitySpotMarket'), ('Price', hourly_nodal_prices_nl_avg)]
    db_emlab.import_objects([('MarketClearingPoints', newobject_mcp_name)])
    db_emlab.import_object_parameter_values(
        [('MarketClearingPoints', newobject_mcp_name, i[0], i[1], str(current_emlab_tick))
         for i in values])
    print('Done exporting MarketClearingPoint to EMLAB')


def crop_dataframe_until_first_empty_row(df):
    """
    This function is used to crop dataframes that have lots of empty rows (with NaN).
    It returns all data until the first row with all NaN values.

    :param df: Dataframe
    :return: Cropped Dataframe
    """
    if df.isnull().values.any():
        first_row_with_all_nan = df.loc[df.iloc[:, 0].isnull(), :].index.tolist()[0]
        return df.loc[0:first_row_with_all_nan - 1]
    else:
        return df


def export_total_sum_exports_to_emlab(db_emlab, hourly_nl_balance_df, current_emlab_tick):
    """
    Export the amount of CO2 tons caused by exports. Estimation: 0.287 is average ton / MWh and 0.47 is average
    efficiency.

    :param db_emlab:
    :param hourly_nl_balance_df:
    :param current_emlab_tick:
    :return:
    """
    db_emlab.import_object_classes(['Exports'])
    db_emlab.import_objects([('Exports', 'Exports')])
    db_emlab.import_data({'object_parameters': [['Exports', 'Exports']]})
    db_emlab.import_object_parameter_values([('Exports', 'Exports', 'Exports',
                                              hourly_nl_balance_df['Exports'].sum() * 0.287 / 0.47,
                                              str(current_emlab_tick))])


def export_all_competes_results():
    """
    This is the main export function
    """

    print('Establishing Database Connections...')
    db_emlab = SpineDB(sys.argv[1])
    db_competes = SpineDB(sys.argv[2])
    print('Done')

    try:
        current_emlab_tick, current_competes_tick, current_competes_tick_rounded = get_current_ticks(db_emlab, 2020)
        print('Current EM-Lab tick: ' + str(current_emlab_tick))
        print('Current COMPETES tick: ' + str(current_competes_tick))

        db_emlab_powerplants, db_emlab_ppdps, db_competes_powerplants, db_emlab_mcps = query_databases(db_emlab,
                                                                                                       db_competes)

        print('Staging next SpineDB alternative...')
        step = 10
        db_emlab.import_alternatives([str(current_emlab_tick + step)])

        path_to_competes_results = sys.argv[3]
        file_name_gentransinv = sys.argv[4].replace('?', str(current_competes_tick))
        file_name_gentransdisp = sys.argv[5].replace('?', str(current_competes_tick))

        print('Loading sheets...')
        hourly_nodal_prices_df, unit_generation_df, new_generation_capacity_df, decommissioning_df, vre_investment_df, \
            hourly_nl_balance_df = read_excel_sheets(path_to_competes_results, file_name_gentransinv,
                                                     file_name_gentransdisp)

        new_generation_capacity_df = crop_dataframe_until_first_empty_row(new_generation_capacity_df)
        vre_investment_df = crop_dataframe_until_first_empty_row(vre_investment_df)
        decommissioning_df = crop_dataframe_until_first_empty_row(decommissioning_df)

        # VRE Plants are added to unit_generation sheet
        hourly_nl_balance_df = hourly_nl_balance_df.rename(columns={'Sun': 'SunPV', 'Wind Onshore': 'WindOn',
                                                                    'Wind Offshore': 'WindOff'})
        unit_generation_df = unit_generation_df.transpose().join(
            hourly_nl_balance_df[['SunPV', 'WindOn', 'WindOff']]).replace(np.nan, 0)
        print('Done loading sheets')

        hourly_nodal_prices_nl = get_hourly_nodal_prices(hourly_nodal_prices_df)
        hourly_nodal_prices_nl = [i if i < 250 else 250 for i in hourly_nodal_prices_nl]    # Limit nodal prices to 250
        export_market_clearing_points_to_emlab(db_emlab, current_emlab_tick, hourly_nodal_prices_nl, db_emlab_mcps)
        export_power_plant_dispatch_plans_to_emlab(db_emlab, current_emlab_tick, unit_generation_df, db_emlab_ppdps,
                                                   hourly_nodal_prices_nl, db_emlab_powerplants)
        export_investment_decisions_to_emlab_and_competes(db_emlab, db_competes, current_emlab_tick,
                                                          new_generation_capacity_df, current_competes_tick, step)
        export_decommissioning_decisions_to_emlab_and_competes(db_competes, db_emlab, db_competes_powerplants,
                                                               decommissioning_df, current_competes_tick,
                                                               current_emlab_tick, step)
        prepare_competes_importer(vre_investment_df, current_competes_tick, path_to_competes_results)
        export_total_sum_exports_to_emlab(db_emlab, hourly_nl_balance_df, current_emlab_tick)

        print('Committing...')
        db_emlab.commit('Imported from COMPETES run ' + str(current_competes_tick))
        db_competes.commit('Imported from COMPETES run ' + str(current_competes_tick))
        print('Done')
    except Exception as e:
        print('Exception occurred: ' + str(e))
        raise
    finally:
        print('Closing database connection...')
        db_emlab.close_connection()
        db_competes.close_connection()


print('===== Starting COMPETES Output Interpretation script =====')
export_all_competes_results()
print('===== End of COMPETES Output Interpretation script =====')
