# encoding: utf-8

import pytest

from fabric.api import env
from fabric.context_managers import settings

from fabfile.instance import add_instance


def test_file_socket():
    env.use_zmq_socket_file = True
    env.roledefs = {
        'eng': ('root@aaa', 'root@bbb')
    }
    instance = add_instance('toto', 'passwd')
    assert instance == env.instances['toto']
    assert instance.zmq_server is None
    assert instance.kraken_engines == ['root@aaa', 'root@bbb']
    assert instance.jormungandr_zmq_socket_for_instance == 'ipc:///srv/kraken/toto/kraken.sock'
    assert instance.kraken_zmq_socket == 'ipc:///srv/kraken/toto/kraken.sock'


def test_missing_zmq_port():
    env.use_zmq_socket_file = False
    with pytest.raises(SystemExit) as excinfo:
        add_instance('toto', 'passwd')
    assert excinfo.value.message == "Instance configuration must include a ZMQ port, aborting " \
                                   "(see fabfile.env.platforms for some instructions)"


def test_localhost_default_server():
    env.use_zmq_socket_file = False
    env.zmq_server = 'localhost'
    env.roledefs = {
        'eng': ('root@aaa', 'root@bbb')
    }
    instance = add_instance('toto', 'passwd', zmq_socket_port=30001)
    assert instance.zmq_server == 'localhost'
    assert instance.kraken_engines == ['root@aaa', 'root@bbb']
    assert instance.jormungandr_zmq_socket_for_instance == 'tcp://localhost:30001'
    assert instance.kraken_zmq_socket == 'tcp://*:30001'


def test_default_server():
    env.use_zmq_socket_file = False
    env.zmq_server = 'vip.truc'
    env.roledefs = {
        'eng': ('root@aaa', 'root@bbb')
    }
    instance = add_instance('toto', 'passwd', zmq_socket_port=30001)
    assert instance.zmq_server == 'vip.truc'
    assert instance.kraken_engines == ['root@aaa', 'root@bbb']
    assert instance.jormungandr_zmq_socket_for_instance == 'tcp://vip.truc:30001'
    assert instance.kraken_zmq_socket == 'tcp://*:30001'


def test_default_server_altered_user():
    env.use_zmq_socket_file = False
    env.zmq_server = 'vip.truc'
    env.roledefs = {
        'eng': ('navitia@aaa', 'navitia@bbb')
    }
    with settings(default_ssh_user='navitia'):
        instance = add_instance('toto', 'passwd', zmq_socket_port=30001)
    assert instance.zmq_server == 'vip.truc'
    assert instance.kraken_engines == ['navitia@aaa', 'navitia@bbb']
    assert instance.jormungandr_zmq_socket_for_instance == 'tcp://vip.truc:30001'
    assert instance.kraken_zmq_socket == 'tcp://*:30001'


def test_default_server_altered_roledefs():
    # check that attribute kraken_engines is a copy from env.roledefs, not a reference
    env.use_zmq_socket_file = False
    env.zmq_server = 'vip.truc'
    env.roledefs = {
        'eng': ('root@aaa', 'root@bbb')
    }
    instance = add_instance('toto', 'passwd', zmq_socket_port=30001)
    env.roledefs['eng'] = []
    assert instance.kraken_engines == ['root@aaa', 'root@bbb']


def test_localhost_zmq_server():
    env.use_zmq_socket_file = False
    env.roledefs = {
        'eng': ('root@aaa', 'root@bbb'),
        'ws': ('root@aaa',)
    }
    instance = add_instance('toto', 'passwd', zmq_socket_port=30001, zmq_server='localhost')
    assert instance.zmq_server == 'localhost'
    assert instance.kraken_engines == ['root@aaa']
    assert instance.jormungandr_zmq_socket_for_instance, 'tcp://localhost:30001'
    assert instance.kraken_zmq_socket == 'tcp://*:30001'


def test_single_zmq_server_noenv():
    env.use_zmq_socket_file = False
    env.zmq_server = None
    env.roledefs = {
        'eng': ('root@aaa', 'root@bbb')
    }
    instance = add_instance('toto', 'passwd', zmq_socket_port=30001, zmq_server='bbb')
    assert instance.zmq_server == 'bbb'
    assert instance.kraken_engines == ['root@bbb']
    assert instance.jormungandr_zmq_socket_for_instance == 'tcp://bbb:30001'
    assert instance.kraken_zmq_socket == 'tcp://*:30001'


def test_single_zmq_server():
    env.use_zmq_socket_file = False
    env.zmq_server = 'vip.truc'
    env.roledefs = {
        'eng': ('root@aaa', 'root@bbb')
    }
    instance = add_instance('toto', 'passwd', zmq_socket_port=30001, zmq_server='bbb')
    assert instance.zmq_server == 'vip.truc'
    assert instance.kraken_engines == ['root@bbb']
    assert instance.jormungandr_zmq_socket_for_instance == 'tcp://vip.truc:30001'
    assert instance.kraken_zmq_socket == 'tcp://*:30001'


def test_multiple_zmq_server():
    env.use_zmq_socket_file = False
    env.zmq_server = 'vip.truc'
    env.roledefs = {
        'eng': ('root@aaa', 'root@bbb', 'root@ccc', 'root@ddd')
    }
    instance = add_instance('toto', 'passwd', zmq_socket_port=30001, zmq_server=('bbb', 'ccc'))
    assert instance.zmq_server == 'vip.truc'
    assert instance.kraken_engines == ['root@bbb', 'root@ccc']
    assert instance.jormungandr_zmq_socket_for_instance == 'tcp://vip.truc:30001'
    assert instance.kraken_zmq_socket == 'tcp://*:30001'
