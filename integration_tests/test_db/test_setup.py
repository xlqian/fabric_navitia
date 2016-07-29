# encoding: utf-8

from ..test_common import skipifdev
from ..utils import get_processes, check_postgres_user, get_databases


@skipifdev
def test_start_services(distributed_undeployed):
    platform, fabric = distributed_undeployed
    value, exception, stdout, stderr = fabric.execute_forked('component.db.start_services')
    assert exception is None
    assert stderr == ''
    assert 'postgres' in get_processes(platform, 'host1')


@skipifdev
def test_setup_db(distributed_undeployed):
    platform, fabric = distributed_undeployed
    value, exception, stdout, stderr = fabric.execute_forked('component.db.setup_db')
    assert exception is None
    assert stderr == ''

    # check postgres users creation
    assert check_postgres_user(platform, fabric.env.tyr_postgresql_user)
    assert check_postgres_user(platform, fabric.env.cities_db_user)
    assert check_postgres_user(platform, fabric.env.postgres_read_only_user)

    # check postgres databases creation
    databases = get_databases(platform, 'host1')
    assert fabric.env.tyr_postgresql_database in databases
    assert fabric.env.cities_db_name in databases


@skipifdev
def test_check_is_postgresql_user_exist(distributed_undeployed):
    platform, fabric = distributed_undeployed
    fabric.execute_forked('component.db.setup_db')
    value, exception, stdout, stderr = fabric.execute_forked('component.db.check_is_postgresql_user_exist',
                                                             fabric.env.tyr_postgresql_user)
    assert exception is None
    assert stderr == ''
    assert value.values()[0]


@skipifdev
def test_create_postgresql_user(distributed_undeployed):
    platform, fabric = distributed_undeployed
    value, exception, stdout, stderr = fabric.execute_forked('component.db.create_postgresql_user', 'toto', 'passwd')
    assert exception is None
    assert stderr == ''

    # check postgres users creation
    check_postgres_user(platform, 'toto')


@skipifdev
def test_create_postgresql_database(distributed_undeployed):
    platform, fabric = distributed_undeployed
    fabric.execute_forked('component.db.create_postgresql_user', 'toto', 'passwd')
    value, exception, stdout, stderr = fabric.execute_forked('component.db.create_postgresql_database', 'toto')
    assert exception is None
    assert stderr == ''

    assert 'toto' in get_databases(platform, 'host1')


@skipifdev
def test_remove_postgresql_database(distributed_undeployed):
    platform, fabric = distributed_undeployed
    fabric.execute_forked('component.db.create_postgresql_user', 'toto', 'passwd')
    fabric.execute_forked('component.db.create_postgresql_database', 'toto')
    assert 'toto' in get_databases(platform, 'host1')

    value, exception, stdout, stderr = fabric.execute_forked('component.db.remove_postgresql_database', 'toto')
    assert exception is None
    assert stderr == ''

    assert 'toto' not in get_databases(platform, 'host1')


@skipifdev
def test_remove_postgresql_user(distributed_undeployed):
    platform, fabric = distributed_undeployed
    fabric.execute_forked('component.db.create_postgresql_user', 'toto', 'passwd')
    assert check_postgres_user(platform, 'toto')

    value, exception, stdout, stderr = fabric.execute_forked('component.db.remove_postgresql_user', 'toto')
    assert exception is None
    assert stderr == ''

    assert not check_postgres_user(platform, 'toto')


@skipifdev
def test_is_postgresql_database_exist(distributed_undeployed):
    platform, fabric = distributed_undeployed
    fabric.execute_forked('component.db.create_postgresql_user', 'toto', 'passwd')
    fabric.execute_forked('component.db.create_postgresql_database', 'toto')

    value, exception, stdout, stderr = fabric.execute_forked('component.db.is_postgresql_database_exist', 'toto')
    assert exception is None
    assert stderr == ''
    assert value.values()[0]


@skipifdev
def test_db_has_postgis(distributed_undeployed):
    platform, fabric = distributed_undeployed
    fabric.execute_forked('component.db.create_postgresql_user', 'toto', 'passwd')
    fabric.execute_forked('component.db.create_postgresql_database', 'toto')

    value, exception, stdout, stderr = fabric.execute_forked('component.db.db_has_postgis', 'toto')
    assert exception is None
    assert stderr == ''
    assert not value.values()[0]

    fabric.execute_forked('component.db.postgis_initdb', 'toto')
    value, exception, stdout, stderr = fabric.execute_forked('component.db.db_has_postgis', 'toto')
    assert exception is None
    assert stderr == ''
    assert value.values()[0]


@skipifdev
def test_create_instance_db(distributed_undeployed):
    platform, fabric = distributed_undeployed

    class instance(object):
        def __init__(self, name):
            self.db_user = name
            self.db_name = name
            self.db_password = name

    value, exception, stdout, stderr = fabric.execute_forked('component.db.create_instance_db', instance('toto'))
    assert exception is None
    assert stderr == ''
    assert 'Really run create_instance_db' in stdout
    assert check_postgres_user(platform, 'toto')
    assert 'toto' in get_databases(platform, 'host1')
