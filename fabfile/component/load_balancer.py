# coding=utf-8

# Copyright (c) 2001-2015, Canal TP and/or its affiliates. All rights reserved.
#
# This file is part of fabric_navitia, the provisioning and deployment tool
#     of Navitia, the software to build cool stuff with public transport.
#
# Hope you'll enjoy and contribute to this project,
#     powered by Canal TP (www.canaltp.fr).
# Help us simplify mobility and open public transport:
#     a non ending quest to the responsive locomotion way of traveling!
#
# LICENCE: This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Stay tuned using
# twitter @navitia
# IRC #navitia on freenode
# https://groups.google.com/d/forum/navitia
# www.navitia.io

"""
This file contains some tasks to manipulate the load balancer
"""
import getpass
from socket import inet_aton, gethostbyname, error
from fabric.colors import red, yellow
from fabric.api import env, task
bigsuds_loaded = False
try:
    import bigsuds
    bigsuds_loaded = True
except ImportError:
    print(yellow("WARNING: can't load bigsuds to manage F5 load balancers"))

from fabfile.utils import get_host_addr


def get_adc_credentials():
    if 'adc_username' not in env:
        print(yellow("Please enter your ADC credentials:"))
        env.adc_username = raw_input("%s username: " % env.ADC_HOSTNAME)
        env.adc_password = getpass.getpass("%s password: " % env.ADC_HOSTNAME)


def _adc_connection(check=False):
    if bigsuds_loaded is True:
        get_adc_credentials()
        connection = bigsuds.BIGIP(
            hostname=env.ADC_HOSTNAME,
            username=env.adc_username,
            password=env.adc_password
            ) 
        if check:
            try:
                connection.System.SystemInfo.get_version()
            except Exception as error:
                print(red("Error when connecting to %s: %s" % (env.ADC_HOSTNAME, error)))
                exit(1)
        return connection
    else:
        print(red("CRITICAL: Can't manage F5 load balancer as 'import bigsuds' fails"))
        exit(1)

@task
def disable_node(server):
    """ Disable F5 ADC node """
    node = _get_adc_nodename(get_host_addr(server))
    connection = _adc_connection()

    print("Disable %s node" % node)
    if env.dry_run is False:
        connection.LocalLB.NodeAddressV2.set_monitor_state(nodes=[node], states=['STATE_DISABLED'])
        connection.LocalLB.NodeAddressV2.set_session_enabled_state(nodes=[node], states=['STATE_DISABLED'])


@task
def enable_node(server):
    """ Enable F5 ADC node """
    node = _get_adc_nodename(get_host_addr(server))
    connection = _adc_connection()

    # Re-enable node globally
    print("Enable %s node" % node)
    if env.dry_run is False:
        connection.LocalLB.NodeAddressV2.set_monitor_state(nodes=[node], states=['STATE_ENABLED'])
        connection.LocalLB.NodeAddressV2.set_session_enabled_state(nodes=[node], states=['STATE_ENABLED'])


def _sync_adc(connection):
    # Sync ADCs configuration
    # detect the fail over device group in the configsync
    # because there are other device groups: device_trust_group and gtm
    device_groups = connection.Management.DeviceGroup.get_list()
    for device_group in device_groups:
        if 'DGT_FAILOVER' in connection.Management.DeviceGroup.get_type(device_groups=[device_group]):
            group = device_group
            break

    device = connection.Management.Device.get_local_device()
    connection.System.ConfigSync.synchronize_to_group_v2(group=group, device=device, force=False)


def _get_adc_nodename(host):
    """Return the ADC node name based on the ip address of given host"""

    # if the host is an ip address
    try:
        inet_aton(host)
        reverse_dns = host
    except error:
        reverse_dns = gethostbyname(host)

    connection = _adc_connection()
    nodes = connection.LocalLB.NodeAddressV2.get_list()
    ipaddress = connection.LocalLB.NodeAddressV2.get_address(nodes)

    for node in zip(nodes, ipaddress):
        if reverse_dns in node:
            return node[0]

    return None
