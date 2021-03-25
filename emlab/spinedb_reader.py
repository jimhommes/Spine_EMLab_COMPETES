#
# This is the Python class responsible for all reads of the SpineDB.
# This is a separate file so that all import definitions are centralized.
#
# Jim Hommes - 25-3-2021
#
from repository import *

class SpineDBReader:

    def __init__(self, db):
        self.db = db

    def read_db_and_create_repository(self):
        reps = Repository()
        return reps