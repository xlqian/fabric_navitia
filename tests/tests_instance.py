# encoding: utf-8

import unittest

from fabric.api import env
from fabric.context_managers import settings

from fabfile.instance import add_instance


class TestInstance(unittest.TestCase):
    def test_file_socket(self):
        env.use_zmq_socket_file = True
        env.roledefs = {
            'eng': ('root@aaa', 'root@bbb')
        }
        instance = add_instance('toto', 'pzekgjp8aeog')
        self.assertEqual(instance, env.instances['toto'])
        self.assertIsNone(instance.zmq_server)
        self.assertEqual(instance.kraken_engines, ['root@aaa', 'root@bbb'])

    def test_missing_zmq_port(self):
        env.use_zmq_socket_file = False
        with self.assertRaises(SystemExit) as arc:
            add_instance('toto', 'pzekgjp8aeog')
        self.assertEqual(arc.exception.args, (1,))

    def test_localhost_default_server(self):
        env.use_zmq_socket_file = False
        env.zmq_server = 'localhost'
        env.roledefs = {
            'eng': ('root@aaa', 'root@bbb')
        }
        instance = add_instance('toto', 'pzekgjp8aeog', zmq_socket_port=30001)
        self.assertEqual(instance.zmq_server, 'localhost')
        self.assertEqual(instance.jormungandr_zmq_socket_for_instance, 'tcp://localhost:30001')
        self.assertEqual(instance.kraken_engines, ['root@aaa', 'root@bbb'])

    def test_default_server(self):
        env.use_zmq_socket_file = False
        env.zmq_server = 'vip.truc'
        env.roledefs = {
            'eng': ('root@aaa', 'root@bbb')
        }
        instance = add_instance('toto', 'pzekgjp8aeog', zmq_socket_port=30001)
        self.assertEqual(instance.zmq_server, 'vip.truc')
        self.assertEqual(instance.jormungandr_zmq_socket_for_instance, 'tcp://vip.truc:30001')
        self.assertEqual(instance.kraken_engines, ['root@aaa', 'root@bbb'])

    def test_default_server_altered_user(self):
        env.use_zmq_socket_file = False
        env.zmq_server = 'vip.truc'
        env.roledefs = {
            'eng': ('navitia@aaa', 'navitia@bbb')
        }
        with settings(default_ssh_user='navitia'):
            instance = add_instance('toto', 'pzekgjp8aeog', zmq_socket_port=30001)
        self.assertEqual(instance.zmq_server, 'vip.truc')
        self.assertEqual(instance.jormungandr_zmq_socket_for_instance, 'tcp://vip.truc:30001')
        self.assertEqual(instance.kraken_engines, ['navitia@aaa', 'navitia@bbb'])

    def test_default_server_altered_roledefs(self):
        env.use_zmq_socket_file = False
        env.zmq_server = 'vip.truc'
        env.roledefs = {
            'eng': ('root@aaa', 'root@bbb')
        }
        instance = add_instance('toto', 'pzekgjp8aeog', zmq_socket_port=30001)
        env.roledefs['eng'] = []
        self.assertEqual(instance.kraken_engines, ['root@aaa', 'root@bbb'])

    def test_localhost_zmq_server(self):
        env.use_zmq_socket_file = False
        env.roledefs = {
            'eng': ('root@aaa', 'root@bbb'),
            'ws': ('root@aaa',)
        }
        instance = add_instance('toto', 'pzekgjp8aeog', zmq_socket_port=30001, zmq_server='localhost')
        self.assertEqual(instance.zmq_server, 'localhost')
        self.assertEqual(instance.jormungandr_zmq_socket_for_instance, 'tcp://localhost:30001')
        self.assertEqual(instance.kraken_engines, ['root@aaa'])

    def test_single_zmq_server(self):
        env.use_zmq_socket_file = False
        env.roledefs = {
            'eng': ('root@aaa', 'root@bbb')
        }
        instance = add_instance('toto', 'pzekgjp8aeog', zmq_socket_port=30001, zmq_server='bbb')
        self.assertEqual(instance.zmq_server, 'bbb')
        self.assertEqual(instance.jormungandr_zmq_socket_for_instance, 'tcp://bbb:30001')
        self.assertEqual(instance.kraken_engines, ['root@bbb'])

    def test_multiple_zmq_server(self):
        env.use_zmq_socket_file = False
        env.zmq_server = 'vip.truc'
        env.roledefs = {
            'eng': ('root@aaa', 'root@bbb', 'root@ccc', 'root@ddd')
        }
        instance = add_instance('toto', 'pzekgjp8aeog', zmq_socket_port=30001, zmq_server=('bbb', 'ccc'))
        self.assertEqual(instance.zmq_server, 'vip.truc')
        self.assertEqual(instance.jormungandr_zmq_socket_for_instance, 'tcp://vip.truc:30001')
        self.assertEqual(instance.kraken_engines, ['root@bbb', 'root@ccc'])


if __name__ == '__main__':
    unittest.main()
