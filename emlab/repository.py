
class Repository:
    def __init__(self, db_data):
        self.energyProducers = {}
        self.powerPlants = {}

        for energyProducer in [i for i in db_data['objects'] if i[0] == 'EnergyProducers']:
            self.energyProducers[energyProducer[1]] = EnergyProducer(energyProducer)

        for energyProducer in self.energyProducers:
            for parameterValue in [i for i in db_data['object_parameter_values'] if i[1] == energyProducer.name]:
                energyProducer.add_parameter_value(parameterValue)

        for powerPlant in [i for i in db_data['objects'] if i[0] == 'PowerPlants']:
            self.powerPlants[powerPlant[1]] = PowerPlant(powerPlant)

        for powerPlant in self.powerPlants:
            for parameterValue in [i for i in db_data['object_parameter_values'] if i[1] == powerPlant.name]:
                powerPlant.add_parameter_value(parameterValue)


class EnergyProducer:
    def __init__(self, import_obj):
        self.name = import_obj[1]
        self.parameters = {}

    def add_parameter_value(self, import_obj):
        self.parameters[import_obj[2]] = import_obj[3]


class PowerPlant:
    def __init__(self, import_obj):
        self.name = import_obj[1]
        self.parameters = {}

    def add_parameter_value(self, import_obj):
        self.parameters[import_obj[2]] = import_obj[3]