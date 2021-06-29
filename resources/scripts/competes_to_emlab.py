"""
This script handles all communication passed from the COMPETES Excel output to the EM-Lab SpineDB.
It handles the MarketClearingPoint from the Hourly Nodal Prices and the unit generation as PowerPlantDispatchPlans.

Jim Hommes - 10-6-2021
"""
import sys
import pandas
from datetime import datetime
from spinedb import SpineDB
from helper_functions import get_current_ticks


def crop_dataframe_until_first_empty_row(df):
    if df.isnull().values.any():
        first_row_with_all_nan = df.loc[df.iloc[:, 0].isnull(), :].index.tolist()[0]
        return df.loc[0:first_row_with_all_nan-1]
    else:
        return df


print('===== Starting COMPETES Output Interpretation script =====')
print('Loading Databases...')
db_emlab = SpineDB(sys.argv[1])
db_competes = SpineDB(sys.argv[2])

try:
    current_emlab_tick, current_competes_tick, current_competes_tick_rounded = get_current_ticks(db_emlab, 2020)
    db_emlab_powerplants = db_emlab.query_object_parameter_values_by_object_class('PowerPlants')
    print('Done loading Databases.')
    print('Current EM-Lab tick: ' + str(current_emlab_tick))
    print('Current COMPETES tick: ' + str(current_competes_tick))

    path_to_competes_results = sys.argv[3]
    file_name_gentrans = sys.argv[4].replace('?', str(current_competes_tick))
    file_name_uc = sys.argv[5].replace('?', str(current_competes_tick))

    print('Loading sheets...')
    hourly_nodal_prices_df = pandas.read_excel(path_to_competes_results + '/' + file_name_gentrans, 'Hourly Nodal Prices')
    unit_generation_df = pandas.read_excel(path_to_competes_results + '/' + file_name_gentrans, 'NL Unit Generation', index_col=0, skiprows=1)
    new_generation_capacity_df = pandas.read_excel(path_to_competes_results + '/' + file_name_gentrans, 'New Generation Capacity', skiprows=2, usecols='A:D,G:X')
    new_generation_capacity_df = crop_dataframe_until_first_empty_row(new_generation_capacity_df)
    vre_investment_df = pandas.read_excel(path_to_competes_results + '/' + file_name_gentrans, 'VRE investment', skiprows=2, usecols='A:D')
    vre_investment_df = crop_dataframe_until_first_empty_row(vre_investment_df)
    print('Done loading sheets')

    print('Exporting MarketClearingPoint to EMLAB')
    hourly_nodal_prices_df.columns = hourly_nodal_prices_df.iloc[0]
    hourly_nodal_prices_df.drop([0])
    hourly_nodal_prices_nl = hourly_nodal_prices_df['NED'][1:].values
    hourly_nodal_prices_nl_avg = sum(hourly_nodal_prices_nl) / len(hourly_nodal_prices_nl)
    print('Average hourly nodal prices: ' + str(hourly_nodal_prices_nl_avg))

    print('Staging...')
    newobject_mcp_name = 'MarketClearingPoint ' + str(datetime.now())
    values = [('Market', 'DutchElectricitySpotMarket'), ('Price', hourly_nodal_prices_nl_avg)]
    db_emlab.import_objects([('MarketClearingPoints', newobject_mcp_name)])
    db_emlab.import_object_parameter_values([('MarketClearingPoints', newobject_mcp_name, i[0], i[1], str(current_emlab_tick))
                                             for i in values])
    print('Done exporting MarketClearingPoint to EMLAB')

    print('Exporting PowerPlantDispatchPlans into EMLAB')
    unit_generation_df = unit_generation_df.transpose()
    ppdp_objects_to_import = []
    ppdp_values_to_import = []
    for power_plant in unit_generation_df.columns:
        print('Staging PPDP for ' + str(power_plant))
        accepted = sum(unit_generation_df[power_plant].values)
        ppdp_name = 'PowerPlantDispatchPlan ' + str(datetime.now())
        ppdp_objects_to_import.append(('PowerPlantDispatchPlans', ppdp_name))
        owner = next(row['parameter_value'] for row in db_emlab_powerplants if row['object_name'] == power_plant and row['parameter_name'] == 'FirmNL')
        status = 'Accepted' if accepted > 0 else 'Failed'
        values = [('AcceptedAmount', accepted), ('Capacity', accepted), ('EnergyProducer', owner), ('Market', 'DutchElectricitySpotMarket'), ('Plant', power_plant), ('Status', status), ('Price', hourly_nodal_prices_nl_avg)]
        ppdp_values_to_import = ppdp_values_to_import + [('PowerPlantDispatchPlans', ppdp_name, i[0], i[1], str(current_emlab_tick)) for i in values]
    db_emlab.import_objects(ppdp_objects_to_import)
    db_emlab.import_object_parameter_values(ppdp_values_to_import)
    print('Done exporting PowerPlantDispatchPlans to EMLAB')

    print('Exporting Investment Decisions to EMLAB and COMPETES...')
    for index, row in new_generation_capacity_df.iterrows():
        print('Export to COMPETES')
        param_values = [i for i in row[4:].items() if i[0] != 'UNITEU']
        plant_name = row['UNITEU']
        print('New plant ' + plant_name + ' with parameters ' + str(param_values))
        db_competes.import_objects([('Installed Capacity Abroad', plant_name)])
        db_competes.import_object_parameter_values([('Installed Capacity Abroad', row['UNITEU'], param_name, param_value) for (param_name, param_value) in param_values])
        print('Done')

        print('If NED export to EMLAB')
        if row['Node'] == 'NED' and float(row['MWEU']) > 0:
            db_emlab.import_objects([('PowerPlants', plant_name)])
            param_values = [(col.replace("EU", "NL"), value) for (col, value) in param_values]
            db_emlab.import_object_parameter_values([('PowerPlants', plant_name, param_index, param_value) for (param_index, param_value) in param_values])
        print('Done')
    print('Done exporting Investment Decisions to EMLAB and COMPETES')

    print('Exporting VRE Investment Decisions to EMLAB and COMPETES...')
    print('Export to EMLAB')
    for index, row in vre_investment_df.iterrows():
        old_mw = next(row['parameter_value'] for row in db_emlab_powerplants if row['object_name'] == row['WindOn'] and row['parameter_name'] == 'MWNL')
        db_emlab.import_object_parameter_values([('PowerPlants', row['WindOn'], 'MWNL', float(old_mw) + float(row['Initial']), '0')])
    print('Done')

    print('Export to COMPETES')
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

    print('Done exporting VRE Investment Decisions to EMLAB and COMPETES')

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
    print('===== End of COMPETES Output Interpretation script =====')
