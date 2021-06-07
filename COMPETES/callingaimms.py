# -*- coding: utf-8 -*-
"""
Created on Fri Apr 23 10:37:40 2021

@author: hernandezsernar
"""

import subprocess
import os
#call COMPETES procedure specific
command = 'C:\Users\\hernandezsernar\\AppData\\Local\\AIMMS\\IFA\\Aimms\\4.79.3.10-x64-VS2017\\Bin\\AimmsCmd.exe "C:\\Users\hernandezsernar\\Documents\\COMPETES\\Competes_2020.aimms" --run-only "examplespine"'


print("running...")
ret = subprocess.call(command, shell=True)
print("done!")