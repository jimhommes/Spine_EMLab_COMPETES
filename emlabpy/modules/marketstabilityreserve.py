from modules.defaultmodule import DefaultModule
from util.repository import Repository


class DetermineMarketStabilityReserveFlow(DefaultModule):
    def __init__(self, reps: Repository):
        super().__init__("Market Stability Reserve: Determine Flows", reps)

    def act(self):
        for msr in self.reps.market_stability_reserves.values():
            print(msr.name)



