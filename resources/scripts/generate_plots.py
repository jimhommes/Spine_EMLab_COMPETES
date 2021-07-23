import matplotlib.pyplot as plt
import os
import pandas
import numpy as np
from spinedb import SpineDB
import pandas as pd


def plot_mcps_with_filter(db_mcps, market, years_to_generate, path_to_plots, title, file_name):
    # MCP Plots
    filtered_mcps = [i['object_name'] for i in db_mcps if i['parameter_name'] == 'Market' and i['parameter_value'] == market]
    mcp_x = []
    mcp_y = []

    print('Creating ' + str(market) + ' MCP plot')
    for row in [i for i in db_mcps if i['object_name'] in filtered_mcps]:
        if row['parameter_name'] == 'Price':
            mcp_x.append(int(row['alternative']) + years_to_generate[0])
            mcp_y.append(row['parameter_value'])

    fig7 = plt.figure()
    axs7 = plt.axes()
    axs7.plot(mcp_x, mcp_y, 'bo')
    plt.xlabel('Years')
    plt.ylabel('Euro / ton')
    axs7.set_title(title)
    fig7.savefig(path_to_plots + '/' + file_name)


def plot_annual_balances(annual_balance, years_to_generate, path_to_plots):
    # Annual Balance
    print('Create Annual Balance plot')
    plt.figure()
    annual_balance_df = pd.DataFrame(annual_balance, index=years_to_generate)
    axs125 = annual_balance_df.plot.bar(stacked=True, rot=0)
    plt.xlabel('Years')
    plt.ylabel('MWh')
    axs125.set_title('NL Annual Balance per Technology')
    fig125 = axs125.get_figure()
    fig125.savefig(path_to_plots + '/' + 'NL Annual Balance.png')


def plot_vre_nl_installed_capacity(vre_investment_sums, years_to_generate, path_to_plots):
    # VRE Investments plot
    print('Create VRE Investments plot')
    plt.figure()
    vre_investments_df = pd.DataFrame(vre_investment_sums, index=years_to_generate)
    axs5 = vre_investments_df.plot.bar(stacked=True, rot=0)
    plt.xlabel('Years')
    plt.ylabel('MW')
    axs5.set_title('NL VRE Installed Capacity')
    fig5 = axs5.get_figure()
    fig5.savefig(path_to_plots + '/' + 'NL VRE Investments.png')


def plot_investments(investment_sums, years_to_generate, path_to_plots):
    # Investments plot
    print('Create Investments plot')
    if len(investment_sums.keys()) > 0:
        plt.figure()
        investments_df = pd.DataFrame(investment_sums, index=years_to_generate)
        axs6 = investments_df.plot.bar(stacked=True, rot=0)
        plt.xlabel('Years')
        plt.ylabel('MW')
        axs6.set_title('NL Investments')
        fig6 = axs6.get_figure()
        fig6.savefig(path_to_plots + '/' + 'NL Investments.png')


def plot_co2_emissions(co2_emission_sums, years_to_generate, path_to_plots):
    # CO2 emissions plot
    print('Create annual CO2 Emission per tech plot')
    plt.figure()
    co2_df = pd.DataFrame(co2_emission_sums, index=years_to_generate)
    axs4 = co2_df.plot.bar(stacked=True, rot=0)
    plt.xlabel('Years')
    plt.ylabel('tons')
    axs4.set_title('NL CO2 Emissions')
    fig4 = axs4.get_figure()
    fig4.savefig(path_to_plots + '/' + 'NL CO2 Emissions.png')


def plot_nl_unit_generation(path_and_filename_dispatch, year, path_to_plots):
    print('Plot NL Unit Generation')
    # Plot 3 NL Unit Generation curve
    nl_unit_generation_df = pandas.read_excel(path_and_filename_dispatch, 'NL Unit Generation', skiprows=1, index_col=0, header=0).transpose()

    plt.figure()
    axs3 = nl_unit_generation_df.plot()
    plt.xlabel('Hours')
    plt.ylabel('MWh')
    plt.legend(fontsize='xx-small', loc='upper left', bbox_to_anchor=(1, 1.1))
    axs3.set_title('NL Unit Generation ' + str(year))
    fig3 = axs3.get_figure()
    fig3.savefig(path_to_plots + '/' + 'NL Unit Generation ' + str(year) + '.png')


def plot_hourly_nodal_price_duration_curve(hourly_nodal_prices_df, year, path_to_plots):
    # Plot 2.5 Hourly Market Price Duration Curve
    print('Create Hourly Nodal Price duration curve')
    plt.figure()
    axs25 = hourly_nodal_prices_df['NED'].sort_values(ascending=False).plot(use_index=False)
    plt.xlabel('Hours')
    plt.ylabel('Euro')
    axs25.set_title('NL Hourly Market Price Duration Curve ' + str(year))
    fig25 = axs25.get_figure()
    fig25.savefig(path_to_plots + '/' + 'NL Nodal Prices Duration Curve ' + str(year) + '.png')


def plot_hourly_nodal_prices(path_and_filename_dispatch, year, path_to_plots):
    # Plot 2 Hourly Nodal Prices
    print('Read and create hourly nodal prices plot')
    hourly_nodal_prices_df = pandas.read_excel(path_and_filename_dispatch, 'Hourly Nodal Prices', skiprows=1, index_col=0)
    hourly_nodal_prices_df[hourly_nodal_prices_df > 250] = 250

    plt.figure()
    axs2 = hourly_nodal_prices_df['NED'].plot()
    plt.xlabel('Hours')
    plt.ylabel('Euro')
    axs2.set_title('NL Hourly Market Prices ' + str(year))
    fig2 = axs2.get_figure()
    fig2.savefig(path_to_plots + '/' + 'NL Nodal Prices ' + str(year) + '.png')

    return hourly_nodal_prices_df


def plot_residual_load_duration_curve(hourly_nl_balance_demand, hourly_nl_balance_df, year, path_to_plots):
    # Plot 1.75: Residual Load Curve
    print('Create Res Load duration curve')
    plt.figure()
    hourly_nl_balance_residual_load = hourly_nl_balance_demand.subtract(hourly_nl_balance_df['Wind Onshore']) \
        .subtract(hourly_nl_balance_df['Wind Offshore']) \
        .subtract(hourly_nl_balance_df['Sun']) \
        .subtract(hourly_nl_balance_df['Hydro Conv.'])
    axs175 = hourly_nl_balance_residual_load.sort_values(ascending=False).plot(use_index=False)
    axs175.set_title('NL Residual Load Duration Curve ' + str(year))
    plt.xlabel('Hours')
    plt.ylabel('MWh')
    fig175 = axs175.get_figure()
    fig175.savefig(path_to_plots + '/' + 'NL Residual Load Duration Curve ' + str(year) + '.png')


def plot_load_duration_curve(hourly_nl_balance_demand, year, path_to_plots):
    # Plot 1.5: Load duration curve
    print('Create Load duration curve plot')
    plt.figure()
    axs15 = hourly_nl_balance_demand.sort_values(ascending=False).plot(use_index=False)
    axs15.set_title('NL Load Duration Curve ' + str(year))
    plt.xlabel('Hours')
    plt.ylabel('MWh')
    fig15 = axs15.get_figure()
    fig15.savefig(path_to_plots + '/' + 'NL Load Duration Curve ' + str(year) + '.png')


def prepare_annual_nl_balance(hourly_nl_balance_df, annual_balance, years_to_generate, year):
    print('Prepare Annual NL Balance plot data')
    hourly_nl_annual = hourly_nl_balance_df.sum()
    for index, col in hourly_nl_annual.iteritems():
        if index in annual_balance.keys():
            annual_balance[index].append(col)
        else:
            annual_balance[index] = [0] * years_to_generate.index(year) + [col]
    return annual_balance


def plot_hourly_nl_balance(path_and_filename_dispatch, path_to_plots, year):
    # Plot 1 Hourly NL Balance (per year)
    print('Read and Create Hourly NL Balance plot')
    hourly_nl_balance_df = pandas.read_excel(path_and_filename_dispatch, 'Hourly NL Balance', skiprows=1, index_col=0, skipfooter=2, usecols='A:R').replace(np.nan, 0)
    hourly_nl_balance_demand = hourly_nl_balance_df['Demand']
    hourly_nl_balance_df = hourly_nl_balance_df.drop(['Demand', 'Exports'], axis=1)

    hourly_nl_balance_df['T'] = hourly_nl_balance_df.sum(axis=1)
    hourly_nl_balance_df = hourly_nl_balance_df.sort_values(by=['T'], ascending=False)
    hourly_nl_balance_df = hourly_nl_balance_df.drop(['T'], axis=1)
    hourly_nl_balance_df = hourly_nl_balance_df.interpolate(method='cubic')
    axs = hourly_nl_balance_df.plot.area(use_index=False)
    axs.set_title('Hourly NL Balance - All Technologies ' + str(year))
    plt.xlabel('Hours')
    plt.ylabel('MWh')
    plt.legend(fontsize='xx-small', loc='upper left', bbox_to_anchor=(1, 1.1))
    fig = axs.get_figure()
    fig.savefig(path_to_plots + '/' + 'NL Hourly Balance ' + str(year) + '.png')
    return hourly_nl_balance_df, hourly_nl_balance_demand


def prepare_co2_emission_data(path_and_filename_dispatch, co2_emission_sums, years_to_generate, year):
    # Preparing values for CO2 Emissions plot, plot after years iterations
    print('Prepare CO2 Emission plot data')
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
    return co2_emission_sums


def prepare_vre_investment_data(path_and_filename_investments, vre_investment_sums, years_to_generate, year):
    # Preparing values for VRE Investments plot, plot after years iterations
    print('Preparing VRE Investment data')
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
    return vre_investment_sums


def prepare_investment_and_decom_data(path_and_filename_investments, investment_sums, years_to_generate, year,
                                      emlab_spine_powerplants_tech_dict):
    print('Loading investment and decom data')
    decommissioning = pandas.read_excel(path_and_filename_investments, 'Decommissioning', skiprows=2, usecols='A:C')
    investments = pandas.read_excel(path_and_filename_investments, 'New Generation Capacity', skiprows=2, usecols="A:D")
    investment_sums = prepare_investment_data(investments, investment_sums, years_to_generate, year)
    investment_sums = prepare_decom_data(decommissioning, emlab_spine_powerplants_tech_dict, investment_sums,
                                         years_to_generate, year, investments)
    return investment_sums


def prepare_decom_data(decommissioning, emlab_spine_powerplants_tech_dict, investment_sums, years_to_generate, year, investments):
    print('Preparing Decom plot data')
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
    return investment_sums


def prepare_investment_data(investments, investment_sums, years_to_generate, year):
    # Preparing values for Investments plot, plot after years iterations
    print('Preparing Investment plot data')
    investments = investments[investments['Node'] == 'NED']
    investments['CombinedIndex'] = [i[0] + ', ' + i[1] for i in zip(investments['FUEL'].values, investments['FuelType'].values)]
    for index, row in investments.iterrows():
        if row['CombinedIndex'] in investment_sums.keys():
            investment_sums[row['CombinedIndex']].append(row['MW'])
        else:
            investment_sums[row['CombinedIndex']] = [0] * years_to_generate.index(year) + [row['MW']]
    return investment_sums


def generate_plots():
    # Select what years you want to generate plots for
    path_to_competes_results = '../../COMPETES/Results'
    filename_to_load_dispatch = 'Output_Dynamic_Gen&Trans_?_Dispatch.xlsx'
    filename_to_load_investment = 'Output_Dynamic_Gen&Trans_?_Investments.xlsx'

    # Create plots directory if it does not exist yet
    path_to_plots = path_to_competes_results + '/plots'
    if not os.path.exists(path_to_plots):
        os.makedirs(path_to_plots)

    years_to_generate = [2020]
    look_ahead = 7

    co2_emission_sums = dict()
    vre_nl_installed_capacity = dict()
    investment_sums = dict()
    annual_balance = dict()

    # EMLab Plots
    print('Establishing and querying SpineDB...')
    spinedb = SpineDB(r"sqlite:///E:\Dropbox\workspace\Spine_EMLab_COMPETES\.spinetoolbox\items\db_emlab\DB.sqlite")
    try:
        emlab_spine_powerplants = spinedb.query_object_parameter_values_by_object_class('PowerPlants')
        emlab_spine_powerplants_tech_dict = {i['object_name']: i['parameter_value'] + ' (D)' for i in emlab_spine_powerplants if i['parameter_name'] == 'TECHTYPENL'}
        db_mcps = spinedb.query_object_parameter_values_by_object_class('MarketClearingPoints')
    finally:
        spinedb.close_connection()
    print('Done')

    # Generate plots
    print('Start generating plots per year')
    for year in years_to_generate:
        print('Preparing and plotting for year ' + str(year))
        path_and_filename_dispatch = path_to_competes_results + '/' + filename_to_load_dispatch.replace('?', str(year))
        path_and_filename_investments = path_to_competes_results + '/' + filename_to_load_investment.replace('?', str(year + look_ahead))

        # Preparing Data
        investment_sums = prepare_investment_and_decom_data(path_and_filename_investments, investment_sums,
                                                            years_to_generate, year, emlab_spine_powerplants_tech_dict)
        vre_nl_installed_capacity = prepare_vre_investment_data(path_and_filename_investments, vre_nl_installed_capacity,
                                                          years_to_generate, year)
        co2_emission_sums = prepare_co2_emission_data(path_and_filename_dispatch, co2_emission_sums, years_to_generate,
                                                      year)

        # Plots
        hourly_nl_balance_df, hourly_nl_balance_demand = plot_hourly_nl_balance(path_and_filename_dispatch,
                                                                                path_to_plots, year)

        # Another prepare data
        annual_balance = prepare_annual_nl_balance(hourly_nl_balance_df, annual_balance, years_to_generate, year)

        # More plots
        plot_load_duration_curve(hourly_nl_balance_demand, year, path_to_plots)
        plot_residual_load_duration_curve(hourly_nl_balance_demand, hourly_nl_balance_df, year, path_to_plots)
        hourly_nodal_prices_df = plot_hourly_nodal_prices(path_and_filename_dispatch, year, path_to_plots)
        plot_hourly_nodal_price_duration_curve(hourly_nodal_prices_df, year, path_to_plots)
        # plot_nl_unit_generation(path_and_filename_dispatch, year, path_to_plots)

    print('Plotting prepared data')
    plot_co2_emissions(co2_emission_sums, years_to_generate, path_to_plots)
    plot_investments(investment_sums, years_to_generate, path_to_plots)
    plot_vre_nl_installed_capacity(vre_nl_installed_capacity, years_to_generate, path_to_plots)
    plot_annual_balances(annual_balance, years_to_generate, path_to_plots)
    plot_mcps_with_filter(db_mcps, 'CO2Auction', years_to_generate, path_to_plots, 'NL CO2 Market Clearing Prices',
                          'NL CO2 Market Clearing Prices.png')
    plot_mcps_with_filter(db_mcps, 'DutchCapacityMarket', years_to_generate, path_to_plots, 'NL Capacity Market Prices',
                          'NL Capacity Market Prices.png')

    print('Showing plots...')
    plt.show()


print('===== Start Generating Plots =====')
generate_plots()
print('===== End Generating Plots =====')