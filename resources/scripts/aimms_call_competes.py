# -*- coding: utf-8 -*-
"""
Created on Fri Apr 23 10:37:40 2021

This script is responsible for running COMPETES by connecting through the DataExchange library that AIMMS offers.
In AIMMS, StartHTTPService has to be running. This means AIMMS is ready to receive REST requests.

Arg1: path to EMLAB SpineDB
Arg2: AIMMS Service Name given to Procedure that runs COMPETES

@author: hernandezsernar
@author: Jim Hommes
"""

import requests
import time
import sys
from spinedb import SpineDB
from helper_functions import get_current_ticks

print('===== Starting COMPETES Execution =====')
print('Read current year from SpineDB...')
db_emlab = SpineDB(sys.argv[1])
try:
    current_emlab_tick, current_competes_tick, current_competes_tick_rounded = get_current_ticks(db_emlab, 2020)
finally:
    db_emlab.close_connection()

aimms_service_name = sys.argv[2]
print('Running AIMMS service ' + aimms_service_name)
port = 8080
url = 'http://localhost'

print('Sending HTTP Request to AIMMS')
result = requests.post(url + ':' + str(port) + '/api/v1/tasks/' + aimms_service_name + '?InputYear=' + str(current_competes_tick))
print('Response Code: ' + str(result.status_code))
print('Response Body: ' + result.text)
request_id = result.json()['id']
print('Activity ID: ' + request_id)

status = requests.get(url + ':' + str(port) + '/api/v1/tasks/' + request_id)
print(status.json())
while status.json()['status'] != 'finished' and status.json()['status'] != 'interrupted':
    print('Current status: ' + status.json()['status'] + ', t=' + status.json()['runtime'])
    time.sleep(5)
    status = requests.get(url + ':' + str(port) + '/api/v1/tasks/' + request_id)
print('Done')
print('Response Code: ' + str(status.status_code))
print('Response Body: ' + status.text)
print('===== End of COMPETES Execution =====')
