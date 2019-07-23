import os
import sys

import pytest

THIS_FILE_DIR = os.path.dirname(os.path.abspath(__file__)) + os.sep
sys.path.append(THIS_FILE_DIR + ".." + os.sep + "..")

from pymsfilereader import MSFileReader


rawfilename_ = THIS_FILE_DIR + "Shew_246a_LCQa_15Oct04_Andro_0904-2_4-20.RAW"


@pytest.fixture(scope="session")
def rawfilename():
    return rawfilename_


@pytest.fixture(scope="session")
def rawfile():
    rawfile = MSFileReader(rawfilename_)
    yield rawfile
    rawfile.Close()


@pytest.fixture(scope="session")
def filters_3_0():
    from .filters_3_0 import filters
    return filters


@pytest.fixture(scope="session")
def filters_3_1():
    from .filters_3_1 import filters
    return filters

@pytest.fixture(scope="session")
def chrodata():
    from .chroData import chrodata
    return chrodata


@pytest.fixture(scope="session")
def statuslogforpos0():
    from .statusLogForPos0 import statuslogforpos0
    return statuslogforpos0


@pytest.fixture(scope="session")
def instmethod():
    from .instMethod import instmethod
    return instmethod
