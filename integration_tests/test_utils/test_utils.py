
# encoding: utf-8

from ..test_common import skipifdev


@skipifdev
def test_downtime(single_undeployed):
    platform, fabric = single_undeployed

    with fabric.set_call_tracker('-utils.login_nagios',
                                 '-utils.stop_supervision') as data:
        value, exception, stdout, stderr = fabric.execute_forked('utils.supervision_downtime', 'kraken', )
    assert exception is None
    assert stderr == ''

    assert len(data()['login_nagios']) == 1
    assert len(data()['stop_supervision']) == 1
