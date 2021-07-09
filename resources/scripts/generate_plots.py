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
filename_to_load = 'Output_Dynamic_Gen&Trans_?.xlsx'
years_to_generate = [2020]

co2_emission_sums = dict()
vre_investment_sums = dict()
investment_sums = dict()

# Generate plots
for year in years_to_generate:
    path_and_filename = path_to_competes_results + '/' + filename_to_load.replace('?', str(year))

    # Perparing values for Investments plot, plot after years iterations
    investments = pandas.read_excel(path_and_filename, 'New Generation Capacity', skiprows=2, usecols="A:D")
    investments = investments[investments['Node'] == 'NED']
    investments['CombinedIndex'] = [i[0] + ', ' + i[1] for i in zip(investments['FUEL'].values, investments['FuelType'].values)]
    for index, row in investments.iterrows():
        if row['CombinedIndex'] in investment_sums:
            investment_sums[row['CombinedIndex']].append(row['MW'])
        else:
            investment_sums[row['CombinedIndex']] = [row['MW']]

    # Preparing values for VRE Investments plot, plot after years iterations
    vre_investments = pandas.read_excel(path_and_filename, 'VRE investment', skiprows=2)
    for index, row in vre_investments[vre_investments['Bus'] == 'NED'].iterrows():
        if row['WindOn'] in vre_investment_sums.keys():
            vre_investment_sums[row['WindOn']].append(row['Initial'])
        else:
            vre_investment_sums[row['WindOn']] = [row['Initial']]

    # Preparing values for CO2 Emissions plot, plot after years iterations
    co2_emissions = pandas.read_excel(path_and_filename, 'CO2 Emissions tech', skiprows=1, index_col=0)
    co2_emissions.columns = [i[0] + ',' + i[1] for i in zip(co2_emissions.columns.values, co2_emissions.iloc[0].values)]

    for index, value in co2_emissions.loc['NED'].iteritems():
        if index in co2_emission_sums.keys():
            co2_emission_sums[index].append(value)
        else:
            co2_emission_sums[index] = [value]

    # Plot 1
    hourly_nl_balance_df = pandas.read_excel(path_and_filename, 'Hourly NL Balance', skiprows=1, index_col=0, skipfooter=2).replace(np.nan, 0)
    axs = hourly_nl_balance_df.plot()
    axs.set_title('Hourly NL Balance - All Technologies')
    plt.xlabel('Hours')
    plt.ylabel('MWh')
    plt.legend(fontsize='xx-small', loc='upper left', bbox_to_anchor=(1, 1.1))
    fig = axs.get_figure()
    fig.savefig(path_to_plots + '/' + 'NL Hourly Balance ' + str(year) + '.png')

    # Plot 2
    hourly_nodal_prices_df = pandas.read_excel(path_and_filename, 'Hourly Nodal Prices', skiprows=1, index_col=0)
    hourly_nodal_prices_df[hourly_nodal_prices_df > 250] = 250

    plt.figure()
    axs2 = hourly_nodal_prices_df['NED'].plot()
    plt.xlabel('Hours')
    plt.ylabel('Euro')
    axs2.set_title('NL Hourly Market Prices')
    fig2 = axs2.get_figure()
    fig2.savefig(path_to_plots + '/' + 'NL Nodal Prices ' + str(year) + '.png')

    # Plot 3
    nl_unit_generation_df = pandas.read_excel(path_and_filename, 'NL Unit Generation', skiprows=1, index_col=0, header=0).transpose()

    plt.figure()
    axs3 = nl_unit_generation_df.plot()
    plt.xlabel('Hours')
    plt.ylabel('MWh')
    plt.legend(fontsize='xx-small', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs3.set_title('NL Unit Generation')
    fig3 = axs3.get_figure()
    fig3.savefig(path_to_plots + '/' + 'NL Unit Generation ' + str(year) + '.png')


# CO2 emissions plot
plt.figure()
co2_df = pd.DataFrame(co2_emission_sums, index=years_to_generate)
axs4 = co2_df.plot.bar(stacked=True, rot=0)
plt.xlabel('Years')
plt.ylabel('tons')
axs4.set_title('NL CO2 Emissions')
fig4 = axs4.get_figure()
fig4.savefig(path_to_plots + '/' + 'NL CO2 Emissions.png')

# VRE Investments plot
plt.figure()
vre_investments_df = pd.DataFrame(vre_investment_sums, index=years_to_generate)
axs5 = vre_investments_df.plot.bar(stacked=True, rot=0)
plt.xlabel('Years')
plt.ylabel('MW')
axs5.set_title('NL VRE Investments')
fig5 = axs5.get_figure()
fig5.savefig(path_to_plots + '/' + 'NL VRE Investments.png')

# Investments plot
plt.figure()
investments_df = pd.DataFrame(investment_sums, index=years_to_generate)
axs6 = investments_df.plot.bar(stacked=True, rot=0)
plt.xlabel('Years')
plt.ylabel('MW')
axs6.set_title('NL Investments')
fig6 = axs6.get_figure()
fig6.savefig(path_to_plots + '/' + 'NL Investments.png')

# EMLab Plots
spinedb = SpineDB("sqlite:///E:\Dropbox\workspace\Spine_EMLab_COMPETES\.spinetoolbox\items\db_emlab\DB.sqlite")
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
    axs7.plot(co2_x, co2_y)
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
    axs8.plot(cm_x, cm_y)
    plt.xlabel('Years')
    plt.ylabel('Euro / MW')
    axs8.set_title('NL Capacity Market Prices')
    fig8.savefig(path_to_plots + '/' + 'NL Capacity Market Prices.png')

except Exception:
    spinedb.close_connection()
    raise

plt.show()
