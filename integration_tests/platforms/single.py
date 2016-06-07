# encoding: utf-8

from fabric.api import env
from fabfile.instance import add_instance
from common import env_common


def single(host):
    env.host_ip = host
    env_common(tyr=(host,), ed=(host,), kraken=(host,), jormun=(host,))
    env.name = 'single'

    env.postgresql_database_host = 'localhost'

    add_instance('default', 'default')
