# -*- coding: utf-8 -*-
"""
Created on Fri Apr 23 10:37:40 2021

@author: hernandezsernar
"""

import requests
import time

print('===== Starting COMPETES Execution =====')
f = open('currentyear.txt')
current_year = f.read()
print('Running for year ' + current_year)

result = requests.post('http://localhost:60117/api/v1/tasks/examplespine?InputYear=' + current_year)
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