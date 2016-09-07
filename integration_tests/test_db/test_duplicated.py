# encoding: utf-8

import time

from ..test_common import skipifdev
from ..utils import get_databases


instances_db = ['ed_fr_cen', 'ed_fr_idf', 'ed_fr_ne_amiens', 'ed_fr_npdc', 'ed_fr_nw', 'ed_us_wa']


# @skipifdev
def test_databases(duplicated):
    platform, fabric = duplicated
    # postgres is really long to warm up !
    time.sleep(20)
    databases = get_databases(platform, 'host1')
    # check existence of instances databases
    for db in instances_db:
        assert db in databases


@skipifdev
def test_postgis_initdb(duplicated):
    platform, fabric = duplicated
    # postgres is really long to warm up !
    time.sleep(20)
    value, exception, stdout, stderr = fabric.execute_forked('component.db.postgis_initdb', 'ed_us_wa')
    assert exception is None
    assert stderr == ''
    assert 'instance ed_us_wa already has postgis, skiping postgis init' in stdout
