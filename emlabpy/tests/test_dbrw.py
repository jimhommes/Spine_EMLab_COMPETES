"""
This file tests the SpineDBReaderWriter class.
This means that the tests either check whether elements have been written or read correctly

Jim Hommes - 26-4-2021
"""
from conftest import *


class TestDBRW:

    def test_init(self, dbrw):
        assert isinstance(dbrw.db, SpineDB)
        assert dbrw.db_url == 'sqlite:///' + path_to_current_spinedb

    def test_read_db_and_create_repository(self, dbrw):
        reps = dbrw.read_db_and_create_repository()

        # PowerPlants
        pp = reps.power_plants['Power Plant 1']
        assert pp.technology == reps.power_generating_technologies['Nuclear PGT']
        assert pp.location == reps.power_grid_nodes['nlNode']
        assert pp.age == 37
        assert pp.owner == reps.energy_producers['Energy Producer NL A']
        assert pp.capacity == 485
        assert pp.efficiency == 0.33
        assert len(reps.power_plants.values()) == 5  # Check total number
        assert reps.power_plants['Power Plant 3'].age == 8  # Random check

        # TriangularTrends
        tt = reps.trends['demandGrowthTrendNL']
        assert tt.top == 1.02
        assert tt.max == 1.03
        assert tt.min == 0.98
        assert tt.values == [1]
        assert len(reps.trends.values()) == 7 + 5 + 33  # Check total number (Triangular + Step + Geo)
        assert reps.trends['fuelOilTrend'].max == 1.04  # Random

        # Substances
        ss = reps.substances['fuelOil']
        assert ss.co2_density == 7.5
        assert ss.energy_density == 11600
        assert ss.quality == 1
        assert ss.trend == reps.trends['fuelOilTrend']
        assert len(reps.substances.values()) == 8
        assert reps.substances['naturalGas'].co2_density == 0.00187

        # PowerGridNodes
        pgn = reps.power_grid_nodes['nlNode']
        assert pgn.parameters['CapacityMultiplicationFactor'] == 1
        assert pgn.parameters['Zone'] == 'nl'
        assert pgn.parameters['hourlyDemandVariableName'] == 'NL'

        # ElectricitySpotMarkets
        esm = reps.electricity_spot_markets['DutchElectricitySpotMarket']
        assert esm.parameters['valueOfLostLoad'] == 2000
        assert esm.parameters['referencePrice'] == 40
        assert not bool(esm.parameters['isAuction'])
        assert esm.parameters['substance'] == 'electricity'
        assert esm.parameters['growthTrend'] == 'demandGrowthTrendNL'

        # CapacityMarkets
        cm = reps.capacity_markets['DutchCapacityMarket']
        assert cm.parameters['InstalledReserveMargin'] == 0.2

        # CO2Auction
        co2auction = reps.co2_markets['CO2Auction']
        assert co2auction.parameters['referencePrice'] == 0

        # EnergyProducers
        ep = reps.energy_producers['Energy Producer NL A']
        assert ep.parameters['investorMarket'] == 'DutchElectricitySpotMarket'

        # StepTrends
        st = reps.trends['co2TaxTrend']
        assert st.duration == 1
        assert st.start == 2
        assert st.min_value == 3
        assert st.increment == 4

        # GeometricTrends
        gt = reps.trends['coalPSCInvestmentCostTimeSeries']
        assert gt.start == 1365530
        assert gt.growth_rate == 0.05

        # PowerGeneratingTechnologies
        pgt = reps.power_generating_technologies['Coal PSC']
        assert pgt.capacity == 750
        assert not pgt.intermittent
        assert pgt.applicable_for_long_term_contract
        assert pgt.peak_segment_dependent_availability == 1
        assert pgt.base_segment_dependent_availability == 1
        assert pgt.maximum_installed_capacity_fraction_per_agent == 0
        assert pgt.maximum_installed_capacity_fraction_in_country == 0
        assert pgt.minimum_fuel_quality == 0.95
        assert pgt.expected_permittime == 1
        assert pgt.expected_leadtime == 4
        assert pgt.expected_lifetime == 40
        assert pgt.fixed_operating_cost_modifier_after_lifetime == 0.05
        assert pgt.minimum_running_hours == 5000
        assert pgt.depreciation_time == 20
        assert pgt.efficiency_time_series == reps.trends['coalPSCEfficiencyTimeSeries']
        assert pgt.fixed_operating_cost_time_series == reps.trends['coalPSCFixedOperatingCostTimeSeries']
        assert pgt.investment_cost_time_series == reps.trends['coalPSCInvestmentCostTimeSeries']
        assert pgt.co2_capture_efficiency == 0
        assert len(reps.power_generating_technologies.values()) == 11

        # PowerGeneratingTechnologyFuel (SubstanceInFuelMix)
        sifm = reps.power_plants_fuel_mix['Coal PSC'][0]
        assert sifm.substance == reps.substances['hardCoal']
        assert sifm.share == 1

    def test_db_objects_to_dict_no_definition(self, dbrw):
        reps = dbrw.read_db_and_create_repository()
        output_dict = {}
        db_objects_to_dict(reps, dbrw.db.export_data(), output_dict, 'PowerGridNodes', PowerGridNode)
        assert len(output_dict.values()) == 1
        assert len(output_dict['nlNode'].parameters.values()) == 4
        assert output_dict['nlNode'].parameters['hourlyDemandObjectClassName'] == 'ldcNLDE-hourly'

    def test_db_objects_to_dict_with_definition(self, dbrw):
        reps = dbrw.read_db_and_create_repository()
        output_dict = {}
        db_objects_to_dict(reps, dbrw.db.export_data(), output_dict, 'PowerPlants', PowerPlant)
        assert len(output_dict.values()) == 5
        assert output_dict['Power Plant 1'].capacity == 485
        assert output_dict['Power Plant 2'].technology == reps.power_generating_technologies['CCGT']

    def test_db_relationships_to_arr(self, dbrw):
        output_arr = []
        db_relationships_to_arr(dbrw.db.export_data(), output_arr, 'TargetInvestorTargets')
        assert len(output_arr) == 2
        assert output_arr[0][0] == 'TargetInvestorNL'
        assert output_arr[0][1] == 'pvTarget'

    def test_stage_object_class(self, dbrw):
        importelement_testname = 'testclass'
        assert importelement_testname not in [i[0] for i in dbrw.db.export_data()['object_classes']]
        dbrw.stage_object_class(importelement_testname)
        assert importelement_testname in [i[0] for i in dbrw.db.export_data()['object_classes']]

    def test_stage_object_classes(self, dbrw):
        importelement_testname = 'testclass_array'
        assert importelement_testname not in [i[0] for i in dbrw.db.export_data()['object_classes']]
        dbrw.stage_object_classes([importelement_testname])
        assert importelement_testname in [i[0] for i in dbrw.db.export_data()['object_classes']]

    def test_stage_object_parameter(self, dbrw):
        importelement_testname = 'testobject_parameter'
        assert importelement_testname not in [i[1] for i in dbrw.db.export_data()['object_parameters']]
        dbrw.stage_object_parameter('testclass', importelement_testname)
        assert importelement_testname in [i[1] for i in dbrw.db.export_data()['object_parameters']]

    def test_stage_object_parameters(self, dbrw):
        importelement_testname = 'testobject_parameter_arr'
        assert importelement_testname not in [i[1] for i in dbrw.db.export_data()['object_parameters']]
        dbrw.stage_object_parameters('testclass', [importelement_testname])
        assert importelement_testname in [i[1] for i in dbrw.db.export_data()['object_parameters']]

    def test_stage_object(self, dbrw):
        importelement_testname = 'testobject'
        assert importelement_testname not in [i[1] for i in dbrw.db.export_data()['objects']]
        dbrw.stage_object('testclass', importelement_testname)
        assert importelement_testname in [i[1] for i in dbrw.db.export_data()['objects']]

    def test_stage_objects(self, dbrw):
        importelement_testname = 'testobject_arr'
        assert importelement_testname not in [i[1] for i in dbrw.db.export_data()['objects']]
        dbrw.stage_objects([('testclass', importelement_testname)])
        assert importelement_testname in [i[1] for i in dbrw.db.export_data()['objects']]

    def test_stage_object_parameter_values(self, dbrw):
        importelement_testname = 'testparametervalue'
        assert importelement_testname not in [i[3] for i in dbrw.db.export_data()['object_parameter_values']]
        dbrw.stage_object_parameter_values('testclass', 'testobject', [('testobject_parameter', importelement_testname)]
                                           , 'init')
        assert importelement_testname in [i[3] for i in dbrw.db.export_data()['object_parameter_values']]

    def test_stage_init_market_clearing_point_structure(self, dbrw):
        assert dbrw.market_clearing_point_object_classname not in [i[0] for i in
                                                                   dbrw.db.export_data()['object_classes']]
        assert not all(x in [i[1] for i in dbrw.db.export_data()['object_parameters']] for x in
                       ['Market', 'Price', 'TotalCapacity'])
        dbrw.stage_init_market_clearing_point_structure()
        assert dbrw.market_clearing_point_object_classname in [i[0] for i in dbrw.db.export_data()['object_classes']]
        assert all(x in [i[1] for i in dbrw.db.export_data()['object_parameters']] for x in
                   ['Market', 'Price', 'TotalCapacity'])

    def test_stage_init_power_plant_dispatch_plan_structure(self, dbrw):
        assert dbrw.powerplant_dispatch_plan_classname not in [i[0] for i in dbrw.db.export_data()['object_classes']]
        assert not all(x in [i[1] for i in dbrw.db.export_data()['object_parameters']] for x in
                       ['Plant', 'Market', 'Price', 'Capacity', 'EnergyProducer', 'AcceptedAmount', 'Status'])
        dbrw.stage_init_power_plant_dispatch_plan_structure()
        assert dbrw.powerplant_dispatch_plan_classname in [i[0] for i in dbrw.db.export_data()['object_classes']]
        assert all(x in [i[1] for i in dbrw.db.export_data()['object_parameters']] for x in
                   ['Plant', 'Market', 'Price', 'Capacity', 'EnergyProducer', 'AcceptedAmount', 'Status'])

    def test_stage_power_plant_dispatch_plan(self, dbrw):
        importelement_testname = 'testppdp'
        assert importelement_testname not in [i[1] for i in dbrw.db.export_data()['object_parameter_values']
                                              if i[0] == dbrw.powerplant_dispatch_plan_classname]
        ppdp = PowerPlantDispatchPlan(importelement_testname)
        ppdp.plant = PowerPlant("testplant")
        ppdp.bidding_market = ElectricitySpotMarket("testmarket")
        ppdp.bidder = EnergyProducer("testbidder")
        dbrw.stage_power_plant_dispatch_plan(ppdp, 'init')
        assert importelement_testname in [i[1] for i in dbrw.db.export_data()['object_parameter_values']
                                          if i[0] == dbrw.powerplant_dispatch_plan_classname]

    def test_stage_market_clearing_point(self, dbrw):
        importelement_testname = 'testmcp'
        assert importelement_testname not in [i[1] for i in dbrw.db.export_data()['object_parameter_values']
                                              if i[0] == dbrw.market_clearing_point_object_classname]
        mcp = MarketClearingPoint(importelement_testname)
        dbrw.stage_market_clearing_point(mcp, 'init')
        assert importelement_testname in [i[1] for i in dbrw.db.export_data()['object_parameter_values']
                                              if i[0] == dbrw.market_clearing_point_object_classname]

    def test_stage_init_alternative(self, dbrw):
        importelement_testname = 'testalternative'
        assert importelement_testname not in [i[0] for i in dbrw.db.export_data()['alternatives']]
        dbrw.stage_init_alternative(importelement_testname)
        assert importelement_testname in [i[0] for i in dbrw.db.export_data()['alternatives']]
