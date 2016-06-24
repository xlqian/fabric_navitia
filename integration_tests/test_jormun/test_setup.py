# encoding: utf-8

from ..test_common import skipifdev


@skipifdev
def test_deploy_jormungandr_instance_conf(duplicated_undeployed):
    platform, fabric = duplicated_undeployed
    # prepare required folder before test
    platform.docker_exec("mkdir -p /etc/jormungandr.d")

    with fabric.set_call_tracker('component.jormungandr.reload_jormun_safe') as data:
        value, exception, stdout, stderr = fabric.execute_forked('component.jormungandr.deploy_jormungandr_instance_conf',
                                                             'us-wa')
    assert exception is None
    # jormungandr is *not* restarted
    assert 'reload_jormun_safe' not in data()
    # the coverage is deployed
    assert platform.path_exists('/etc/jormungandr.d/us-wa.json', 'host1')


@skipifdev
def test_remove_jormungandr_instance(duplicated_undeployed):
    platform, fabric = duplicated_undeployed
    # prepare required folder before test
    platform.docker_exec("mkdir -p /etc/jormungandr.d")

    fabric.execute_forked('component.jormungandr.deploy_jormungandr_instance_conf', 'us-wa')

    with fabric.set_call_tracker('component.jormungandr.reload_jormun_safe') as data:
        value, exception, stdout, stderr = fabric.execute_forked('component.jormungandr.remove_jormungandr_instance',
                                                                 'us-wa')
    assert exception is None
    # jormungandr is restarted
    assert len(data()['reload_jormun_safe']) == 1
    # the coverage is removed
    assert platform.path_exists('/etc/jormungandr.d/us-wa.json', 'host1', negate=True)


@skipifdev
def test_deploy_jormungandr_all_instances_conf(duplicated_undeployed):
    platform, fabric = duplicated_undeployed
    # prepare required folder before test
    platform.docker_exec("mkdir -p /etc/jormungandr.d")

    with fabric.set_call_tracker('component.jormungandr.reload_jormun_safe',
                                 'component.jormungandr.deploy_jormungandr_instance_conf') as data:
        value, exception, stdout, stderr = \
            fabric.execute_forked('component.jormungandr.deploy_jormungandr_all_instances_conf')
    assert exception is None
    # jormungandr is restarted
    assert len(data()['reload_jormun_safe']) == 1
    # all coverages are deployed
    assert len(data()['deploy_jormungandr_instance_conf']) == len(fabric.env.instances)
    for instance in fabric.env.instances:
        assert platform.path_exists('/etc/jormungandr.d/{}.json'.format(instance), 'host1')


@skipifdev
def test_deploy_jormungandr_include(duplicated_undeployed):
    platform, fabric = duplicated_undeployed
    # prepare required folder before test
    platform.docker_exec("mkdir -p /etc/jormungandr.d")

    fabric.execute('include', 'us-wa')

    with fabric.set_call_tracker('component.jormungandr.reload_jormun_safe',
                                 'component.jormungandr.deploy_jormungandr_instance_conf') as data:
        value, exception, stdout, stderr = \
            fabric.execute_forked('component.jormungandr.deploy_jormungandr_all_instances_conf')
    assert exception is None
    # jormungandr is restarted
    assert len(data()['reload_jormun_safe']) == 1
    # only the included coverage is deployed
    assert len(data()['deploy_jormungandr_instance_conf']) == 1
    for instance in fabric.env.instances:
        assert platform.path_exists('/etc/jormungandr.d/{}.json'.format(instance), 'host1',
                                    negate=(instance != 'us-wa'))
