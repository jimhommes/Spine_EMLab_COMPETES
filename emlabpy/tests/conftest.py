from util.spinedb_reader_writer import *
import pytest

path_to_spinedb = \
    'sqlite:///E:\\Dropbox\\workspace\\Spine_EMLab_COMPETES\\emlabpy\\tests\\.spinetoolbox\\items\\db\\testDB.sqlite'

dbrwvar = SpineDBReaderWriter(path_to_spinedb)


@pytest.fixture(scope="module")
def dbrw():
    return dbrwvar


@pytest.fixture(scope="module")
def reps(dbrw):
    return dbrw.read_db_and_create_repository()
