# -*- coding: utf-8 -*-
"""
Created on Fri Apr 23 10:37:40 2021

@author: hernandezsernar
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

result = requests.post('http://localhost:60117/api/v1/tasks/examplespine?InputYear=' + str(current_competes_tick))
print('Code: ' + str(result.status_code))
print('Body: ' + result.text)
request_id = result.json()['id']
print('ID: ' + request_id)

status = requests.get('http://localhost:60117/api/v1/tasks/' + request_id)
print(status.json())
while status.json()['status'] == 'executing':
    print('Still executing, waiting...')
    time.sleep(5)
    status = requests.get('http://localhost:60117/api/v1/tasks/' + request_id)
print(status.text)
print('Done!')
print('===== End of COMPETES Execution =====')