# encoding: utf-8

import time

from ..test_common import skipifdev


instances_names = {'us-wa', 'fr-nw', 'fr-npdc', 'fr-ne-amiens', 'fr-idf', 'fr-cen'}


@skipifdev
def test_upgrade_kraken(duplicated):
    platform, fabric = duplicated

    with fabric.set_call_tracker('-component.kraken.upgrade_engine_packages',
                                 '-component.kraken.upgrade_monitor_kraken_packages',
                                 'component.kraken.restart_kraken_on_host',
                                 'component.kraken.require_monitor_kraken_started') as data:
        fabric.execute_forked(
            'tasks.upgrade_kraken', kraken_wait=False, up_confs=False, supervision=False)

    assert len(data()['upgrade_engine_packages']) == 2
    assert len(data()['upgrade_monitor_kraken_packages']) == 2
    assert len(data()['require_monitor_kraken_started']) == 2
    assert len(data()['restart_kraken_on_host']) == 2 * len(fabric.env.instances)
    assert len(set((x[0][1] for x in data()['restart_kraken_on_host']))) == 2
    assert set((x[0][0].name for x in data()['restart_kraken_on_host'])) == instances_names


@skipifdev
def test_upgrade_kraken_restricted(duplicated):
    platform, fabric = duplicated
    # patch the eng role (as done in upgrade_all on prod platform)
    fabric.env.roledefs['eng'] = fabric.env.eng_hosts_1

    with fabric.set_call_tracker('-component.kraken.upgrade_engine_packages',
                                 '-component.kraken.upgrade_monitor_kraken_packages',
                                 'component.kraken.restart_kraken_on_host',
                                 'component.kraken.require_monitor_kraken_started') as data:
        fabric.execute_forked(
            'tasks.upgrade_kraken', kraken_wait=False, up_confs=False, supervision=False)

    # upgrades apply only on restricted pool
    assert len(data()['upgrade_engine_packages']) == 1
    assert len(data()['upgrade_monitor_kraken_packages']) == 1
    assert len(data()['require_monitor_kraken_started']) == 1
    # kraken restart apply only on restricted pool
    assert len(data()['restart_kraken_on_host']) == len(fabric.env.instances)
    assert set((x[0][1] for x in data()['restart_kraken_on_host'])) == {fabric.env.eng_hosts_1[0]}
    assert set((x[0][0].name for x in data()['restart_kraken_on_host'])) == instances_names


# @skipifdev
def test_upgrade_all_load_balancer(duplicated):
    platform, fabric = duplicated
    fabric.env.use_load_balancer = True
    # postgres is really long to warm up !
    time.sleep(15)

    with fabric.set_call_tracker('-tasks.check_last_dataset',
                                 '-tasks.upgrade_tyr',
                                 '-tasks.upgrade_kraken',
                                 '-tasks.upgrade_jormungandr',
                                 '-prod_tasks.disable_nodes',
                                 '-prod_tasks.enable_nodes',
                                 '-component.load_balancer._adc_connection',
                                 '-component.load_balancer.disable_node',
                                 '-component.load_balancer.enable_node') as data:
        value, exception, stdout, stderr = fabric.execute_forked('tasks.upgrade_all',
                       check_version=False, kraken_wait=False, check_dead=False)

    assert exception is None
    assert stderr == ''
    assert stdout.count("Executing task 'stop_tyr_beat'") == 1
    assert stdout.count("Executing task 'start_tyr_beat'") == 1
    assert len(data()['disable_nodes']) == 4
    assert len(data()['enable_nodes']) == 3
    assert len(data()['upgrade_jormungandr']) == 2
    assert len(data()['upgrade_kraken']) == 2
    assert len(data()['upgrade_tyr']) == 1
