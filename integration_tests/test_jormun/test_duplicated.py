# encoding: utf-8

import time

from ..test_common import skipifdev
from ..test_common.test_kraken import _start_and_check_krakens


nominal_krakens = {'host1': {'us-wa', 'fr-nw', 'fr-npdc', 'fr-ne-amiens', 'fr-idf', 'fr-cen'},
                   'host2': {'us-wa', 'fr-nw', 'fr-npdc', 'fr-ne-amiens', 'fr-idf', 'fr-cen'}}


@skipifdev
def test_test_jormun(duplicated):
    _start_and_check_krakens(duplicated, nominal_krakens)
    platform, fabric = duplicated

    value, exception, stdout, stderr = fabric.execute_forked('component.jormungandr.test_jormungandr', platform.get_hosts()['host1'],
                          'us-wa', fail_if_error=False)

    assert value.values()[0]
    assert exception is None
    assert 'WARNING: Problem on result' not in stdout

    fabric.execute('stop_kraken', 'us-wa')
    time.sleep(1)

    value, exception, stdout, stderr = fabric.execute_forked('component.jormungandr.test_jormungandr', platform.get_hosts()['host1'],
                          'us-wa', fail_if_error=False)
    assert value.values()[0] is False
    assert exception is None
    assert "WARNING: Problem on result: '{u'message': u'The region %s is dead', u'error': " \
           "{u'message': u'The region %s is dead', u'id': u'dead_socket'}}'" % ('us-wa', 'us-wa') in stdout
    platform.ssh('service apache2 stop')
    time.sleep(1)
    value, exception, stdout, stderr = fabric.execute_forked('component.jormungandr.test_jormungandr', platform.get_hosts()['host1'],
                                                             'us-wa', fail_if_error=True)
    assert type(exception) is SystemExit


