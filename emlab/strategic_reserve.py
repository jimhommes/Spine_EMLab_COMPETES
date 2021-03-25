#
# Strategic Reserve recreated from EM-Lab.
#

import sys
import random
import json
from repository import *
from spinedb import SpineDB
from datetime import datetime

# Input DB
db_url = sys.argv[1]
db = SpineDB(db_url)
db_data = db.export_data()

# Create Objects from the DB Data in the Repository
reps = Repository(db_data)

# Create the DB Object structure for the PPDPs
db.import_object_classes(['PowerPlantDispatchPlans'])
db.import_data({'object_parameters': [['PowerPlantDispatchPlans', 'Market']]})
db.import_data({'object_parameters': [['PowerPlantDispatchPlans', 'Price']]})
db.import_data(
    {'object_parameters': [['PowerPlantDispatchPlans', 'Capacity']]})
db.import_data(
    {'object_parameters': [['PowerPlantDispatchPlans', 'EnergyProducer']]})
# import reserve price and volume
db.import_data({'object_parameters': [['Scenario', 'reserveVolume']]})
db.import_data({'object_parameters': [['Scenario', 'reservePrice']]})

# For every energy producer we will submit bids to the Strategic reserve

db.commit('EM-Lab Strategic Reserve: Submit Bids: ' + str(datetime.now()))

# calculate peak demand
# peakLoadforMarketNOtrend = reps.peakLoadbyZoneMarketandTime(curZone, market)
# trend = market.getDemandGrowthTrend();
# peakLoadforMarket = trend * peakLoadforMarketNOtrend;
# strategicReserveOperatorReserveVolume= peakLoadforMarket * strategicReserveOperator.getReserveVolumePercentSR()

# if Revenues from EOM >  money =  getActualFixedOperatingCost()) + Loan)


isORMarketCleared = false
sumofContractedBids = 0
volumetobeContracted = strategicReserveOperator.getReserveVolume()
clearingEpsilon = 0.001
dispatchPrice = strategicReserveOperator.getReservePriceSR()

if (volumetobeContracted == 0) {
    isORMarketCleared = true}
else if (isORMarketCleared == false) {
    # if not enough volume is contracted contract
    if (volumetobeContracted - (sumofContractedBids + currentPPDP.getAmount()) >= clearingEpsilon) {
        sumofContractedBids += currentPPDP.getAmount()
        currentPPDP.setOldPrice(currentPPDP.getPrice())
        currentPPDP.setPrice(dispatchPrice)

        # pays O&M costs to the generated for the contracted capacity
        Loan = 0
        if ((currentPPDP.getPowerPlant().getLoan().getTotalNumberOfPayments() - currentPPDP.getPowerPlant().getLoan().getNumberOfPaymentsDone()) > 0) {
            Loan = (currentPPDP.getPowerPlant().getLoan().getAmountPerPayment())}
        money = ((currentPPDP.getPowerPlant(
        ).getActualFixedOperatingCost()) + Loan) / segmentCounter
        getReps().createCashFlow(strategicReserveOperator, currentPPDP.getBidder(),
                                 money, CashFlow.STRRESPAYMENT, getCurrentTick(), currentPPDP.getPowerPlant())
    }
    # if enough volume is contracted contract partially the last volume
} else if (volumetobeContracted - (sumofContractedBids + currentPPDP.getAmount()) < clearingEpsilon) {
    currentPPDP.setSRstatus(PowerPlantDispatchPlan.PARTLY_CONTRACTED)
    sumofContractedBids += currentPPDP.getAmount()
    currentPPDP.setOldPrice(currentPPDP.getPrice())
    currentPPDP.setPrice(dispatchPrice)
    isORMarketCleared = true
    # pays O&M costs to the generated for the contracted capacity
    Loan = 0
    if ((currentPPDP.getPowerPlant().getLoan().getTotalNumberOfPayments() - currentPPDP.getPowerPlant().getLoan().getNumberOfPaymentsDone()) > 0) {
        Loan = (currentPPDP.getPowerPlant().getLoan().getAmountPerPayment())
    }
    money = ((currentPPDP.getPowerPlant(
    ).getActualFixedOperatingCost()) + Loan) / segmentCounter
    getReps().createCashFlow(strategicReserveOperator, currentPPDP.getBidder(),
                             money, CashFlow.STRRESPAYMENT, getCurrentTick(), currentPPDP.getPowerPlant())
}
else {
    currentPPDP.setSRstatus(PowerPlantDispatchPlan.NOT_CONTRACTED)
}
