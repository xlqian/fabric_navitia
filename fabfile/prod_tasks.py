from fabric.colors import blue
from fabric.tasks import execute
from fabfile.component import jormungandr, load_balancer
from fabric.api import env, task


def vip_name(instance):
    """ Return kraken vip name based on our convention """

    # ex.: UK-PRD-ENG, TEST-DEV-ENG
    return "{instance}-{env}-ENG" \
            .format(instance=instance.upper(),
                    env=env.name.upper().replace('PROD', 'PRD'))

@task
def remove_kraken_vip(name):
    """ Delete a given instance vip and associated pool """

    pool_name = vip_name(name)
    vs_name = pool_name

    connection = load_balancer._adc_connection()

    print(blue("Delete virtual server %s" % vs_name))
    connection.LocalLB.VirtualServer.delete_virtual_server([vs_name])

    print(blue("Delete pool %s" % pool_name))
    connection.LocalLB.Pool.delete_pool([pool_name])


###################################################
#
#         LOAD BALANCERS MANAGEMENT TASKS
#
# First refactored in commit e725a2571b8bc.
# WARNING
# For the (dis)(en)abling of a kraken node to take
# effect, it is necessary to restart the jormun nodes
# that are enabled.
# So, some rules must be respected:
# 1- enable/disable kraken nodes first,
# 2- enable/disable jormun nodes, and if enabled,
#    restart it before (not mandatory).
# 3- last, restart any jormun that is enabled and
#    has not been restarted in step 2.
#
###################################################


@task
def disable_nodes(nodes):
    for node in nodes:
        execute(load_balancer.disable_node, node)

@task
def enable_nodes(nodes):
    for node in nodes:
        execute(load_balancer.enable_node, node)

@task
def restart_jormungandr(nodes, safe=True, reverse=False):
    for node in (nodes[::-1] if reverse else nodes):
        execute(jormungandr.reload_jormun_safe, node, safe)

@task
def switch_to_first_phase(eng_hosts_1, ws_hosts_1, ws_hosts_2):
    execute(disable_nodes, eng_hosts_1)
    execute(restart_jormungandr, ws_hosts_2)
    execute(disable_nodes, ws_hosts_1)

@task
def switch_to_second_phase(eng_hosts_1, eng_hosts_2, ws_hosts_1,  ws_hosts_2):
    # first, enable / disable kraken nodes
    execute(enable_nodes, eng_hosts_1)
    execute(disable_nodes, eng_hosts_2)
    # then enable / disable jormun nodes and restart active jormun nodes
    execute(restart_jormungandr, ws_hosts_1, safe=False)
    execute(enable_nodes, ws_hosts_1)
    execute(disable_nodes, ws_hosts_2)

@task
def enable_all_nodes(eng_hosts, ws_hosts):
    execute(enable_nodes, eng_hosts)
    execute(restart_jormungandr, ws_hosts, reverse=True)
