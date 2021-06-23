# -*- coding: utf-8 -*-
"""
Created on Fri Apr 23 10:37:40 2021

@author: hernandezsernar
"""

import requests

result = requests.post('http://localhost:60117/api/v1/tasks/examplespine', json={'inputYear': '2020'})
print(result)
