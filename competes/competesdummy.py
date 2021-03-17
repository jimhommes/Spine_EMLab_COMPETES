#
# Dummy file to simulate a COMPETES output.
# Just generates random numbers and adds this to the SpineDB.
#
# Jim Hommes - 17-3-2021
#

import sys
import random
from spinedb import SpineDB

# Input DB
input_db_url = sys.argv[1]
input_db = SpineDB(input_db_url)

# Output DB
output_db_url = sys.argv[2]
output_db = SpineDB(output_db_url)

# Reading SegmentLength
input_db_data = input_db.export_data()
segmentLength_parameterValueObject = [obj[3] for obj in input_db_data['object_parameter_values'] if obj[0] == 'emlabModel' and obj[1] == 'emlabModel' and obj[2] == 'SimulationLength']
segmentLength = int(segmentLength_parameterValueObject[0])


def addRandomness(number):
    return number + ((random.random() - 0.5) * 2)


output = [round(addRandomness(i), 2) for i in range(1, segmentLength)]
output_db.import_object_parameter_values([('actualOutput', 'actualOutput', 'hourlyDemand', {'type': 'time_series', 'data': output})])
