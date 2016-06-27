# encoding: utf-8

from fabric.api import env
import fabfile
from fabfile.instance import add_instance
from common import env_common


def single(host):
    env.host_ip = host
    env_common(tyr=(host,), ed=(host,), kraken=(host,), jormun=(host,))
    env.name = 'single'

    env.postgresql_database_host = 'localhost'

    env.supervision_handler = fabfile.utils.\
        ThrukSupervisionHandler(thruk_backends=[0, 1, 2, 3], ga='ga',
                                url="url", user='user', pwd='pwd', backend='backend',
                                host_support='host_support', token='token')
    env.supervision_config = dict(
        tyr_beat=dict(
            downtime=1,
            hosts=env.roledefs['tyr_master'],
            service='process_tyr_beat'
        ),
        bina=dict(
            downtime=2,
            hosts=env.roledefs['tyr'],
            service='data_ed_{instance}'
        ),
        kraken=dict(
            downtime=3,
            hosts=env.roledefs['ws'],
            service='kraken_{instance}'
        )
    )

    add_instance('default', 'default')
