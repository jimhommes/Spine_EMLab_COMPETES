from util.spinedb_reader_writer import *
from conftest import *
import pytest


class TestDBRW:

    def test_init(self, dbrw):
        assert isinstance(dbrw.db, SpineDB)
        assert dbrw.db_url == path_to_spinedb

    def test_read_db_and_create_repository(self, reps):
        # PowerPlants
        pp = reps.power_plants['Power Plant 1']
        assert pp.technology == reps.power_generating_technologies['Nuclear PGT']
        assert pp.location == reps.power_grid_nodes['nlNode']
        assert pp.age == 37
        assert pp.owner == reps.energy_producers['Energy Producer NL A']
        assert pp.capacity == 485
        assert pp.efficiency == 0.33
        assert len(reps.power_plants.values()) == 5             # Check total number
        assert reps.power_plants['Power Plant 3'].age == 8      # Random check

        # TriangularTrends
        tt = reps.trends['demandGrowthTrendNL']
        assert tt.top == 1.02
        assert tt.max == 1.03
        assert tt.min == 0.98
        assert tt.values == [1]
        assert len(reps.trends.values()) == 7 + 5 + 33          # Check total number (Triangular + Step + Geo)
        assert reps.trends['fuelOilTrend'].max == 1.04          # Random

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


