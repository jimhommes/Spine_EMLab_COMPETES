# -*- coding: utf-8 -*-
"""
Created on Fri Apr  9 14:14:36 2021

@author: ra-COMPETES
"""

import subprocess
import os
#call COMPETES procedure specific
command = 'C:\\Users\\hernandezsernar\\AppData\\Local\\AIMMS\\IFA\\Aimms\\4.79.3.10-x64-VS2017\\Bin\\AimmsCmd.exe "C:\\Users\\hernandezsernar\\Documents\\COMPETES\\Competes_2020.aimms" --run-only "examplespine"'


print("running...")
ret = subprocess.call(command, shell=True)
print("done!")
# log_file = open('log.txt','r')
# print(log_file.read())
# log_file.close()
#"C:\\Users\\ra-COMPETES\\AppData\\Local\\AIMMS\\IFA\\Aimms\\4.76.7.12-x64-VS2017\\Bin\\AimmsCmd.exe" "D:\\OneDrive\\OneDrive - TNO\\Documents\\_DemandResponseCompetes(2020)TradeRES\\Competes_2020.aimms"--run-only examplespine
#--run-only examplespine --end-user



#C:\Users\hernandezsernar\AppData\Local\AIMMS\IFA\Aimms\4.79.3.10-x64-VS2017\Bin\AimmsCmd.exe C:\Users\hernandezsernar\Documents\COMPETES\Competes_2020.aimms --run-only "examplespine"