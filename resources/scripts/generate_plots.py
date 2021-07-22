import matplotlib.pyplot as plt
import os
import pandas
import numpy as np
from spinedb import SpineDB


# Create directory if it does not exist yet
import pandas as pd

path_to_plots = '../plots'
if not os.path.exists(path_to_plots):
    os.makedirs(path_to_plots)

# Select what years you want to generate plots for
path_to_competes_results = '../../COMPETES/Results'
filename_to_load_dispatch = 'Output_Dynamic_Gen&Trans_?_Dispatch.xlsx'
filename_to_load_investment = 'Output_Dynamic_Gen&Trans_?_Investments.xlsx'
years_to_generate = [2020]
look_ahead = 7

co2_emission_sums = dict()
vre_investment_sums = dict()
investment_sums = dict()
annual_balance = dict()

# EMLab Plots
spinedb = SpineDB("sqlite:///E:\Dropbox\workspace\Spine_EMLab_COMPETES\.spinetoolbox\items\db_emlab\DB.sqlite")
try:
    emlab_spine_powerplants = spinedb.query_object_parameter_values_by_object_class('PowerPlants')
    emlab_spine_powerplants_tech_dict = {i['object_name']: i['parameter_value'] + ' (D)' for i in emlab_spine_powerplants if i['parameter_name'] == 'TECHTYPENL'}
except Exception as e:
    spinedb.close_connection()
    raise

# Generate plots
for year in years_to_generate:
    path_and_filename_dispatch = path_to_competes_results + '/' + filename_to_load_dispatch.replace('?', str(year))
    path_and_filename_investments = path_to_competes_results + '/' + \
                                    filename_to_load_investment.replace('?', str(year + look_ahead))

    # Preparing values for Investments plot, plot after years iterations
    investments = pandas.read_excel(path_and_filename_investments, 'New Generation Capacity', skiprows=2, usecols="A:D")
    investments = investments[investments['Node'] == 'NED']
    investments['CombinedIndex'] = [i[0] + ', ' + i[1] for i in zip(investments['FUEL'].values, investments['FuelType'].values)]
    for index, row in investments.iterrows():
        if row['CombinedIndex'] in investment_sums.keys():
            investment_sums[row['CombinedIndex']].append(row['MW'])
        else:
            investment_sums[row['CombinedIndex']] = [0] * years_to_generate.index(year) + [row['MW']]

    decommissioning = pandas.read_excel(path_and_filename_investments, 'Decommissioning', skiprows=2, usecols='A:C')
    decommissioning = decommissioning[decommissioning['node'] == 'NED']
    decommissioning['Technology'] = [emlab_spine_powerplants_tech_dict[i] for i in decommissioning['unit'].values]
    decommissioning_grouped_and_summed = decommissioning.groupby('Technology')['MW'].sum()
    for tech, mw_sum in decommissioning_grouped_and_summed.iteritems():
        if tech in investment_sums.keys():
            investment_sums[tech].append(-1 * mw_sum)
        else:
            investment_sums[tech] = [0] * years_to_generate.index(year) + [-1 * mw_sum]
    # Add 0 to values if not in COMPETES results
    for key in investment_sums.keys():
        if key not in investments['CombinedIndex'].values and key not in decommissioning_grouped_and_summed.index:
            investment_sums[key].append(0)

    # Preparing values for VRE Investments plot, plot after years iterations
    vre_investments = pandas.read_excel(path_and_filename_investments, 'VRE investment', skiprows=2)
    for index, row in vre_investments[vre_investments['Bus'] == 'NED'].iterrows():
        if row['WindOn'] in vre_investment_sums.keys():
            vre_investment_sums[row['WindOn']].append(row['Initial'])
        else:
            vre_investment_sums[row['WindOn']] = [0] * years_to_generate.index(year) + [row['Initial']]
    # Add 0 to values if not in COMPETES results
    for key in vre_investment_sums.keys():
        if key not in vre_investments[vre_investments['Bus'] == 'NED']['WindOn'].values:
            vre_investment_sums[key].append(0)

    # Preparing values for CO2 Emissions plot, plot after years iterations
    co2_emissions = pandas.read_excel(path_and_filename_dispatch, 'CO2 Emissions tech', skiprows=1, index_col=0)
    co2_emissions.columns = [i[0] + ',' + i[1] for i in zip(co2_emissions.columns.values, co2_emissions.iloc[0].values)]

    for index, value in co2_emissions.loc['NED'].iteritems():
        if index in co2_emission_sums.keys():
            co2_emission_sums[index].append(value)
        else:
            co2_emission_sums[index] = [0] * years_to_generate.index(year) + [value]
    # Add 0 to values if not in COMPETES results
    for key in co2_emission_sums.keys():
        if key not in co2_emissions.columns.values:
            co2_emission_sums[key].append(0)

    # Plot 1
    hourly_nl_balance_df = pandas.read_excel(path_and_filename_dispatch, 'Hourly NL Balance', skiprows=1, index_col=0, skipfooter=2, usecols='A:R').replace(np.nan, 0)
    hourly_nl_balance_demand = hourly_nl_balance_df['Demand']
    hourly_nl_balance_df = hourly_nl_balance_df.drop(['Demand', 'Exports'], axis=1)

    hourly_nl_balance_df['T'] = hourly_nl_balance_df.sum(axis=1)
    hourly_nl_balance_df = hourly_nl_balance_df.sort_values(by=['T'], ascending=False)
    hourly_nl_balance_df = hourly_nl_balance_df.drop(['T'], axis=1)
    axs = hourly_nl_balance_df.plot.bar(stacked=True, rot=0, width=1)
    axs.set_title('Hourly NL Balance - All Technologies ' + str(year))
    plt.xlabel('Hours')
    plt.ylabel('MWh')
    plt.legend(fontsize='xx-small', loc='upper left', bbox_to_anchor=(1, 1.1))
    fig = axs.get_figure()
    fig.savefig(path_to_plots + '/' + 'NL Hourly Balance ' + str(year) + '.png')

    # Plot 1.25
    hourly_nl_annual = hourly_nl_balance_df.sum()
    for index, col in hourly_nl_annual.iteritems():
        if index in annual_balance.keys():
            annual_balance[index].append(col)
        else:
            annual_balance[index] = [col]

    # Plot 1.5
    plt.figure()
    axs15 = hourly_nl_balance_demand.sort_values(ascending=False).plot(use_index=False)
    axs15.set_title('NL Load Duration Curve ' + str(year))
    plt.xlabel('Hours')
    plt.ylabel('MWh')
    fig15 = axs15.get_figure()
    fig15.savefig(path_to_plots + '/' + 'NL Load Duration Curve ' + str(year) + '.png')

    # Plot 1.75
    plt.figure()
    hourly_nl_balance_residual_load = hourly_nl_balance_demand.subtract(hourly_nl_balance_df['Wind Onshore'])\
        .subtract(hourly_nl_balance_df['Wind Offshore'])\
        .subtract(hourly_nl_balance_df['Sun'])\
        .subtract(hourly_nl_balance_df['Hydro Conv.'])
    axs175 = hourly_nl_balance_residual_load.sort_values(ascending=False).plot(use_index=False)
    axs175.set_title('NL Residual Load Duration Curve ' + str(year))
    plt.xlabel('Hours')
    plt.ylabel('MWh')
    fig175 = axs175.get_figure()
    fig175.savefig(path_to_plots + '/' + 'NL Residual Load Duration Curve ' + str(year) + '.png')

    # Plot 2
    hourly_nodal_prices_df = pandas.read_excel(path_and_filename_dispatch, 'Hourly Nodal Prices', skiprows=1, index_col=0)
    hourly_nodal_prices_df[hourly_nodal_prices_df > 250] = 250

    plt.figure()
    axs2 = hourly_nodal_prices_df['NED'].plot()
    plt.xlabel('Hours')
    plt.ylabel('Euro')
    axs2.set_title('NL Hourly Market Prices ' + str(year))
    fig2 = axs2.get_figure()
    fig2.savefig(path_to_plots + '/' + 'NL Nodal Prices ' + str(year) + '.png')

    # Plot 2.5
    plt.figure()
    axs25 = hourly_nodal_prices_df['NED'].sort_values(ascending=False).plot(use_index=False)
    plt.xlabel('Hours')
    plt.ylabel('Euro')
    axs25.set_title('NL Hourly Market Price Duration Curve ' + str(year))
    fig25 = axs25.get_figure()
    fig25.savefig(path_to_plots + '/' + 'NL Nodal Prices Duration Curve ' + str(year) + '.png')

    # Plot 3
    # nl_unit_generation_df = pandas.read_excel(path_and_filename_dispatch, 'NL Unit Generation', skiprows=1, index_col=0, header=0).transpose()
    #
    # plt.figure()
    # axs3 = nl_unit_generation_df.plot()
    # plt.xlabel('Hours')
    # plt.ylabel('MWh')
    # plt.legend(fontsize='xx-small', loc='upper left', bbox_to_anchor=(1, 1.1))
    # axs3.set_title('NL Unit Generation ' + str(year))
    # fig3 = axs3.get_figure()
    # fig3.savefig(path_to_plots + '/' + 'NL Unit Generation ' + str(year) + '.png')


# CO2 emissions plot
plt.figure()
co2_df = pd.DataFrame(co2_emission_sums, index=years_to_generate)
axs4 = co2_df.plot.bar(stacked=True, rot=0)
plt.xlabel('Years')
plt.ylabel('tons')
axs4.set_title('NL CO2 Emissions')
fig4 = axs4.get_figure()
fig4.savefig(path_to_plots + '/' + 'NL CO2 Emissions.png')

# Investments plot
plt.figure()
investments_df = pd.DataFrame(investment_sums, index=years_to_generate)
axs6 = investments_df.plot.bar(stacked=True, rot=0)
plt.xlabel('Years')
plt.ylabel('MW')
axs6.set_title('NL Investments')
fig6 = axs6.get_figure()
fig6.savefig(path_to_plots + '/' + 'NL Investments.png')

# VRE Investments plot
plt.figure()
vre_investments_df = pd.DataFrame(vre_investment_sums, index=years_to_generate)
axs5 = vre_investments_df.plot.bar(stacked=True, rot=0)
plt.xlabel('Years')
plt.ylabel('MW')
axs5.set_title('NL VRE Investments')
fig5 = axs5.get_figure()
fig5.savefig(path_to_plots + '/' + 'NL VRE Investments.png')

# Annual Balance
plt.figure()
annual_balance_df = pd.DataFrame(annual_balance, index=years_to_generate)
axs125 = annual_balance_df.plot.bar(stacked=True, rot=0)
plt.xlabel('Years')
plt.ylabel('MWh')
axs125.set_title('NL Annual Balance per Technology')
fig125 = axs125.get_figure()
fig125.savefig(path_to_plots + '/' + 'NL Annual Balance.png')



try:
    db_mcps = spinedb.query_object_parameter_values_by_object_class('MarketClearingPoints')
    co2_mcps = [i['object_name'] for i in db_mcps if i['parameter_name'] == 'Market' and i['parameter_value'] == 'CO2Auction']
    cm_mcps = [i['object_name'] for i in db_mcps if i['parameter_name'] == 'Market' and i['parameter_value'] == 'DutchCapacityMarket']

    co2_x = []
    co2_y = []

    for row in [i for i in db_mcps if i['object_name'] in co2_mcps]:
        if row['parameter_name'] == 'Price':
            co2_x.append(int(row['alternative']) + 2020)
            co2_y.append(row['parameter_value'])

    fig7 = plt.figure()
    axs7 = plt.axes()
    axs7.plot(co2_x, co2_y, 'bo')
    plt.xlabel('Years')
    plt.ylabel('Euro / ton')
    axs7.set_title('NL CO2 Prices')
    fig7.savefig(path_to_plots + '/' + 'NL CO2 Prices.png')

    cm_x = []
    cm_y = []

    for row in [i for i in db_mcps if i['object_name'] in cm_mcps]:
        if row['parameter_name'] == 'Price':
            cm_x.append(int(row['alternative']) + 2020)
            cm_y.append(row['parameter_value'])

    fig8 = plt.figure()
    axs8 = plt.axes()
    axs8.plot(cm_x, cm_y, 'bo')
    plt.xlabel('Years')
    plt.ylabel('Euro / MW')
    axs8.set_title('NL Capacity Market Prices')
    fig8.savefig(path_to_plots + '/' + 'NL Capacity Market Prices.png')

except Exception:
    spinedb.close_connection()
    raise

plt.show()
