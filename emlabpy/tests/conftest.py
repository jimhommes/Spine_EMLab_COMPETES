"""
This is the test configuration file.
Most important is the initialization (copy) of the SpineToolbox test SpineDB which is created through the
Spine Project in the /tests folder. This is copied and all operations are tested.

Jim Hommes - 26-4-2021
"""
from util.spinedb_reader_writer import *
from shutil import copyfile
import pytest
import os

dbcounter = 0
path_to_original_spinedb = '.spinetoolbox\\items\\db\\testDB.sqlite'
path_to_current_spinedb = 'resources\\current_test_spineDB.sqlite'

# Initialization: copy the DB created by Spine to the tests folder for testing
# This way testing always starts with a fresh database.
dirname = os.path.dirname(__file__)
copyfile(os.path.join(dirname, path_to_original_spinedb), os.path.join(dirname, path_to_current_spinedb))


@pytest.fixture(scope="class")
def dbrw():
    """
    This fixture passes the database itself as a parameter to the test.
    :return: DBRW
    """
    dbrw = SpineDBReaderWriter('sqlite:///' + path_to_current_spinedb)
    yield dbrw
    dbrw.db.close_connection()
