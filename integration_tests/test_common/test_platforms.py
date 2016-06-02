# encoding: utf-8

from collections import defaultdict

from fabric.api import env

from fabfile.env.platforms import use

from . import skipifdev


class DuplicateZMQPort(defaultdict):
    def __init__(self, instances):
        defaultdict.__init__(self, list)
        for k, v in instances.iteritems():
            self[v.kraken_zmq_socket.rsplit(':', 1)[1]].append(k)

    def check(self):
        for k, v in self.iteritems():
            assert len(v) == 1, 'zmq_socket_port {}: hosts {}'.format(k, v)


class KrakenCounter(defaultdict):
    """ Count kraken_engines by types for all instances in a platform
    """
    def __init__(self, instances, *kraken_engines):
        defaultdict.__init__(self, int)
        for instance in instances.itervalues():
            for i, kraken in enumerate(kraken_engines):
                if instance.kraken_engines == kraken:
                    self[i] += 1


@skipifdev
def test_prod_setup():
    env.instances = {}
    use('prod')
    assert len(env.instances) == 67
    assert env.use_zmq_socket_file is False
    DuplicateZMQPort(env.instances).check()
    for instance in env.instances.itervalues():
        assert instance.zmq_server == env.zmq_server
    kc = KrakenCounter(env.instances, env.eng_hosts, env.eng_hosts[:2], env.eng_hosts[2:])
    assert kc[0] == 65
    assert kc[1] == 1
    assert kc[2] == 1


@skipifdev
def test_pre_setup():
    env.instances = {}
    use('pre')
    assert len(env.instances) == 67
    assert env.use_zmq_socket_file is False
    DuplicateZMQPort(env.instances).check()
    for instance in env.instances.itervalues():
        assert instance.zmq_server == env.zmq_server
    kc = KrakenCounter(env.instances, env.eng_hosts, env.roledefs['eng'][:1], env.roledefs['eng'][1:])
    assert kc[0] == 0
    assert kc[1] == 33
    assert kc[2] == 34


@skipifdev
def test_sim_setup():
    env.instances = {}
    use('sim')
    assert len(env.instances) == 45
    assert env.use_zmq_socket_file is False
    DuplicateZMQPort(env.instances).check()
    for instance in env.instances.itervalues():
        assert instance.zmq_server == env.zmq_server
        assert instance.kraken_engines == env.roledefs['eng']


@skipifdev
def test_internal_setup():
    env.instances = {}
    use('internal')
    assert len(env.instances) == 25
    assert env.use_zmq_socket_file is False
    DuplicateZMQPort(env.instances).check()
    for instance in env.instances.itervalues():
        assert instance.zmq_server == env.zmq_server
        assert instance.kraken_engines == env.roledefs['eng']


@skipifdev
def test_customer_setup():
    env.instances = {}
    use('customer')
    assert len(env.instances) == 25
    assert env.use_zmq_socket_file is False
    DuplicateZMQPort(env.instances).check()
    for instance in env.instances.itervalues():
        assert instance.zmq_server == env.zmq_server
        assert instance.kraken_engines == env.roledefs['eng']
