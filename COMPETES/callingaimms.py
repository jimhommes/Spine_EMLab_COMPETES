# -*- coding: utf-8 -*-
"""
Created on Fri Apr 23 10:37:40 2021

@author: hernandezsernar
"""

import subprocess
from subprocess import CalledProcessError
import os
import sys

# Retrieve paths from Spine
path_to_aimms = sys.argv[1]
path_to_competes = sys.argv[2]
procedure_name = 'examplespine'

# Call COMPETES procedure specific
command = path_to_aimms + ' "' + path_to_competes + '" --run-only "' + procedure_name + '"'

print("Running command: " + command)
try:
    output = subprocess.check_output(command)
    print(output)
except CalledProcessError as err:
	print('----- Execution failed -----')
	print(err)
	print('----- Please execute COMPETES manually. Type "done" once another year has been executed -----')
	line = input()
	while line != 'done':
		line = input()
print("done!")