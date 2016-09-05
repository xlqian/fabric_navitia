# encoding: utf-8

import os.path
import time

from ..test_common import skipifdev
from ..utils import get_path_attribute

ROOTDIR = os.path.dirname(os.path.abspath(__file__))

instances_names = {'us-wa', 'fr-nw', 'fr-npdc', 'fr-ne-amiens', 'fr-idf', 'fr-cen'}


@skipifdev
def test_tyr_setup(duplicated):
    platform, fabric = duplicated
    assert platform.path_exists('/var/log/tyr')
    assert platform.path_exists('/srv/ed/data')
    assert platform.path_exists('/etc/tyr.d')
    for krak in instances_names:
        assert platform.path_exists('/srv/ed/{}'.format(krak))


@skipifdev
def test_create_remove_tyr_instance(duplicated):
    platform, fabric = duplicated
    fabric.get_object('instance.add_instance')('toto', 'passwd',
                       zmq_socket_port=30004, zmq_server=fabric.env.host1_ip)
    # postgres is really long to warm up !
    time.sleep(15)

    with fabric.set_call_tracker('component.db.create_instance_db') as data:
        value, exception, stdout, stderr = fabric.execute_forked('create_tyr_instance', 'toto')
    assert exception is None
    assert stderr == ''

    # create_instance_db should be called only once
    assert len(data()['create_instance_db']) == 2
    assert stdout.count('Really run create_instance_db') == 1
    # tyr and db instances are created on both machines
    assert stdout.count("Executing task 'create_tyr_instance'") == 2
    assert stdout.count("Executing task 'create_instance_db'") == 2
    assert platform.path_exists('/srv/ed/data/toto')
    assert platform.path_exists('/srv/ed/data/toto/backup')
    assert platform.path_exists('/srv/ed/toto')
    assert platform.path_exists('/var/log/tyr/toto.log')
    assert platform.path_exists('/etc/tyr.d/toto.ini')
    assert platform.path_exists('/srv/ed/toto/alembic.ini')
    assert platform.path_exists('/srv/ed/toto/settings.sh')

    time.sleep(2)
    with fabric.set_call_tracker('component.tyr.restart_tyr_worker',
                                 'component.tyr.restart_tyr_beat') as data:
        value, exception, stdout, stderr = fabric.execute_forked('remove_tyr_instance', 'toto', purge_logs=True)

    assert exception is None
    assert stderr == ''
    assert stdout.count("Executing task 'remove_tyr_instance'") == 2
    assert platform.path_exists('/etc/tyr.d/toto.ini', negate=True)
    assert platform.path_exists('/var/log/tyr/toto.log', negate=True)
    # restart_tyr_worker is called on both machines (good)
    assert len(data()['restart_tyr_worker']) == 2
    assert set((x[2] for x in data()['restart_tyr_worker'])) == set(fabric.env.roledefs['tyr'])
    # restart_tyr_beat is called twice on tyr_master (not so good)
    assert len(data()['restart_tyr_beat']) == 2
    assert set((x[2] for x in data()['restart_tyr_beat'])) == set(fabric.env.roledefs['tyr_master'])


@skipifdev
def test_launch_rebinarization(duplicated):
    platform, fabric = duplicated
    platform.scp(os.path.join(ROOTDIR, 'data.zip'), '/srv/ed/data/us-wa/', 'host1')
    # wait first binarization by tyr (automatic)
    time.sleep(30)
    assert platform.path_exists('/srv/ed/data/us-wa/data.zip', 'host1', negate=True)
    assert platform.path_exists('/srv/ed/data/us-wa/data.nav.lz4', 'host1')
    platform.docker_exec('rm -f /srv/ed/data/us-wa/data.nav.lz4', 'host1')

    value, exception, stdout, stderr = fabric.execute_forked('component.tyr.launch_rebinarization', 'us-wa')
    assert exception is None
    assert stderr == ''
    time.sleep(15)
    assert platform.path_exists('/srv/ed/data/us-wa/data.nav.lz4', 'host1')

    value, exception, stdout, stderr = fabric.execute_forked('component.tyr.launch_rebinarization',
                                                             'us-wa', use_temp=True)
    assert exception is None
    assert stderr == ''
    time.sleep(15)
    assert platform.path_exists('/srv/ed/data/us-wa/temp/data.nav.lz4', 'host1')


@skipifdev
def test_normalize_data_files(duplicated):
    platform, fabric = duplicated
    for instance in instances_names:
        platform.docker_exec('touch /srv/ed/data/{}/data.nav.lz4'.format(instance), 'host1')

    value, exception, stdout, stderr = fabric.execute_forked('component.tyr.normalize_data_files')
    assert exception is None
    assert stderr == ''

    for instance in instances_names:
        path = '/srv/ed/data/{}/data.nav.lz4'.format(instance)
        assert get_path_attribute(platform, path, 'user', 'host1')[0] == 'www-data'
        assert get_path_attribute(platform, path, 'rights', 'host1')[0] == '-rw-r--r--'


# @skipifdev
def test_launch_rebinarization_upgrade(duplicated):
    platform, fabric = duplicated
    platform.scp(os.path.join(ROOTDIR, 'data.zip'), '/srv/ed/data/us-wa/', 'host1')
    # wait first binarization by tyr (automatic)
    time.sleep(30)
    assert platform.path_exists('/srv/ed/data/us-wa/data.zip', 'host1', negate=True)
    assert platform.path_exists('/srv/ed/data/us-wa/data.nav.lz4', 'host1')
    platform.docker_exec('rm -f /srv/ed/data/us-wa/data.nav.lz4', 'host1')

    value, exception, stdout, stderr = fabric.execute_forked('component.tyr.launch_rebinarization_upgrade',
                                                             pilot_supervision=False, pilot_tyr_beat=False,
                                                             instances=('us-wa',))
    assert exception is None
    assert stderr == ''
