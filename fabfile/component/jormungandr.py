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

import StringIO
import ConfigParser
from io import BytesIO
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import ConnectionError
from simplejson.scanner import JSONDecodeError
from time import sleep
from urllib2 import HTTPError

from fabric.colors import red, green, blue, yellow
from fabric.context_managers import settings
from fabric.contrib.files import exists
from fabric.decorators import roles
from fabric.operations import run, get
from fabric.api import execute, task, env, sudo
from fabtools import require

from fabfile.component import kraken, load_balancer
from fabfile.utils import (_install_packages, _upload_template,
                           start_or_stop_with_delay, get_bool_from_cli, get_host_addr)


@task
@roles('ws')
def update_jormungandr_conf():
    """
    update the jormungandr configuration
    """
    require.files.directories([env.jormungandr_base_dir, env.jormungandr_instances_dir, env.jormungandr_log_dir],
                              owner=env.KRAKEN_USER, group=env.KRAKEN_USER, use_sudo=True)

    _upload_template('jormungandr/jormungandr.wsgi.jinja', env.jormungandr_wsgi_file,
                     context={
                         'env': env
                     })
    _upload_template('jormungandr/settings.py.jinja', env.jormungandr_settings_file,
                     context={'env': env})


@task
@roles('ws')
def setup_jormungandr():
    require.users.user('www-data')

    execute(update_jormungandr_conf)

    if env.setup_apache:
        sudo('sudo a2enmod rewrite')
        _upload_template('jormungandr/jormungandr_apache_config.jinja', env.jormungandr_apache_config_file,
                     context={'env': env}, backup=False)

    execute(start_jormungandr_all)

@task
@roles('ws')
#@runs_once
def upgrade_ws_packages():
    packages = [
        'apache2',
        'libapache2-mod-wsgi',
        'logrotate',
        'redis-server',
        'python2.7',
        'git',
        'gcc',
        'python-dev',
        'protobuf-compiler'
    ]
    if env.distrib in ('ubuntu14.04', 'debian8'):
        packages.append('libzmq3-dev')
    elif env.distrib == 'debian7':
        packages.append('libzmq-dev')

    require.deb.packages(packages)
    package_filter_list = ['navitia-jormungandr*deb',
                           'navitia-common*deb']
    _install_packages(package_filter_list)
    require.python.install_pip()

    require.python.install_requirements('/usr/share/jormungandr/requirements.txt',
            use_sudo=True,
            exists_action='w')


@task
def get_jormungandr_config(server, instance):
    """Get jormungandr configuration of a given instance"""

    with settings(host_string=server):
        config_path = instance.jormungandr_config_file

        # first get the configfile here
        temp_file = StringIO.StringIO()
        if exists(config_path):
            get(config_path, temp_file)
        else:
            print(red("ERROR: can't find %s" % config_path))
            exit(1)

        config = ConfigParser.RawConfigParser(allow_no_value=True)
        config.readfp(BytesIO(temp_file.getvalue()))

        if 'instance' in config.sections():
            return config
        else:
            return None

# TODO: testme and putme
@task
def set_jormungandr_config(server, instance, key=None, socket=None,
        cheap_journey=None):
    """ Use the given kraken in the jormungandr server
        This is really useful for testing upgrades in production
    """

    with settings(host_string=server):
        # get the remote config file and localy change it, put it after
        # better than just sed() directly remote
        remote_config = get_jormungandr_config(server, instance)

        with open('/tmp/testinstance', 'wb') as configfile:
            remote_config.write(configfile)

        local_config = ConfigParser.ConfigParser()
        local_config.read('/tmp/testinstance')

        if key:
            local_config.set('instance', 'key', key)
        if socket:
            local_config.set('instance', 'socket', socket)
        if cheap_journey:
            local_config.set('functional', 'cheap_journey', cheap_journey)

        with open('/tmp/testinstance', 'wb') as configfile:
            local_config.write(configfile)

        # finally, put the local on remote dest
        #put('/tmp/testinstance', )

@task
def reload_jormun_safe(server, safe=True):
    """ Reload jormungandr on a specific server,
        in a safe way if load balancers are available
    """
    safe = get_bool_from_cli(safe)
    with settings(host_string=server):
        if env.use_load_balancer and safe:
            load_balancer.disable_node(server)
        sudo("service apache2 reload")
        sleep(1)
        if env.use_load_balancer and safe:
            load_balancer.enable_node(server)

@task
def reload_jormun_safe_all(safe=True, reverse=False):
    """ Reload jormungandr on all servers,
        in a safe way if load balancers are available
    """
    safe = get_bool_from_cli(safe)
    for server in (env.roledefs['ws'][::-1] if reverse else env.roledefs['ws']):
        execute(reload_jormun_safe, server, safe)

@task
def start_jormungandr_all():
    """ Start jormungadr on all servers """
    start_services()
    for server in env.roledefs['ws']:
        execute(reload_jormun_safe, server, False)

@task
@roles('ws')
def start_services():
    start_or_stop_with_delay('apache2', env.APACHE_START_DELAY * 1000, 500, only_once=env.APACHE_START_ONLY_ONCE)

@task
def check_kraken_jormun_after_deploy(server=env.ws_hosts, instance=None):
    headers = {'Host': env.jormungandr_url}

    print("→ server: {}".format(server))
    request_str = 'http://{}/v1/status'.format(get_host_addr(server))
    print("request_string: {}".format(request_str))

    try:
        response = requests.get(request_str, headers=headers)
    except (ConnectionError, HTTPError) as e:
        print(red("HTTP Error %s: %s" % (e.code, e.readlines()[0])))
        exit(1)
    except Exception as e:
        print(red("Error when connecting to %s: %s" % (env.jormungandr_url, e)))
        exit(1)

    try:
        result = response.json()
    except JSONDecodeError:
        print(red("cannot read json response : {}".format(response.text)))
        exit(1)

    if not (result['kraken_version'] is None):
        print "status={} && kraken_version={}".format(result['status'], result['kraken_version'])
    else:
        print "status={}".format(result['status'])

@task
def test_jormungandr(server, instance=None, fail_if_error=True):
    """
    Test jormungandr globally (/v1/coverage) or a given instance

    Note: we don't launch that with a role because we want to test the access from the outside of the server
    """
    headers = {'Host': env.jormungandr_url}

    if instance:
        request_str = 'http://{s}/v1/coverage/{i}/status'.format(s=server, i=instance)
    else:
        request_str = 'http://{}/v1/coverage'.format(server)

    try:
        response = requests.get(request_str, headers=headers, auth=HTTPBasicAuth(env.token, ''))
    except (ConnectionError, HTTPError) as e:
        if fail_if_error:
            print(red("HTTP Error %s: %s" % (e.code, e.readlines()[0])))
            exit(1)
        else:
            print(yellow("WARNING: {instance} is running but "
                "problem found: {error} (maybe no data ?)"
                .format(instance=instance, error=e)))
            exit(0)
    except Exception as e:
        print(red("Error when connecting to %s: %s" % (env.jormungandr_url, e)))
        exit(1)

    try:
        result = response.json()
    except JSONDecodeError:
        print(red("cannot read json response : {}".format(response.text)))
        exit(1)

    # if result contain just a message, this indicate a problem
    if 'message' in result:
        print(fail_if_error)
        print(type(fail_if_error))
        if fail_if_error is True:
            print(red("CRITICAL: Problem on result: '{}'".format(result)))
            exit(1)
        print(yellow("WARNING: Problem on result: '{}'".format(result)))
        return False

    if instance:
        print("%s" % result['status'])
        kraken_version = result['status']['kraken_version']
        if kraken_version != env.version:
            #TODO change this version number handling, it should be automatic and not manually set in env.version
            print(yellow("WARNING: Version of kraken (%s) is not the expected %s" %
                 (kraken_version, env.version)))
        else:
            print(green("OK: Version is %s" % kraken_version))
    # just check that there is one instance running
    else:
        regions = result['regions']

        active_instance = [i for i in env.instances.keys() if i not in env.excluded_instances]
        if len(regions) != len(active_instance):
            print red("there is not the right number of instances, "
                      "we should have {ref} but we got {real} instances".
                      format(ref=len(active_instance), real=len(regions)))
            print red('instances in diff: {}'.format(
                set(active_instance).symmetric_difference(set([r['id'] for r in regions]))))
            if fail_if_error:
                exit(1)
            return False
        else:
            #we check that at least one is ok
            statuses = [(r['id'], r['status']) for r in regions]

            if all(map(lambda p: p[1] == 'running', statuses)):
                print green('all instances are ok, everything is fine')
                return True

            print blue('running instances: {}'.format([r[0] for r in statuses if r[1] == 'running']))
            print red('KO instances: {}'.format([r for r in statuses if r[1] != 'running']))

            if fail_if_error:
                exit(1)
            return False

    return True


@task()
@roles('ws')
def deploy_jormungandr_instance_conf(instance):

    _upload_template("jormungandr/jormungandr.ini.jinja",
                     instance.jormungandr_config_file,
                     context={
                         'env': env,
                         'instance': instance,
                     },
                     use_sudo=True
    )

@task
@roles('ws')
def create_jormungandr_instance(instance, cheap_journey=False):
    #DEPRECATED
    """Create a jormungandr instance
        * Deploy /etc/jormungadr.d/<instance>.ini template
        * Reload apache
    """

    # get the port config from the kraken engine
    config = kraken.get_kraken_config(env.roledefs['eng'][0], instance)
    zmq_socket = config.get('GENERAL', 'zmq_socket')
    instance_port = env.KRAKEN_RE_PORT.match(zmq_socket)
    port = instance_port.group('port')

    _upload_template("jormungandr/jormungandr.ini.jinja",
                     instance.jormungandr_config_file,
                     context={
                         'env': env,
                         'instance': instance,
                         'socket': "tcp://{}:{}".format(env.jormungandr_instance_socket, port),
                         'cheap_journey': cheap_journey,
                     },
                     use_sudo=True
    )

    # testing if instance appears in JSON return on URI /v1/coverage on each
    # Jormungandr
    headers = {'Host': env.jormungandr_url }

    server = env.host_string
    print("→ server: {}".format(server))
    execute(reload_jormun_safe, server)
    request_str = 'http://{}/v1/coverage/{}/status'.format(get_host_addr(server), instance)
    print("request_string: {}".format(request_str))

    try:
        response = requests.get(request_str, headers=headers)
    except (ConnectionError, HTTPError) as e:
        print(red("HTTP Error %s: %s" % (e.code, e.readlines()[0])))
        exit(1)
    except Exception as e:
        print(red("Error when connecting to %s: %s" % (env.jormungandr_url, e)))
        exit(1)

    try:
        result = response.json()
    except JSONDecodeError:
        print(red("cannot read json response : {}".format(response.text)))
        exit(1)

    if result['status']['kraken_version']:
        print(green("OK: Test {} OK".format(instance)))

    # really test the instance, warning, maybe no data so 503 returned
    test_jormungandr(get_host_addr(env.host_string), instance, fail_if_error=False)

@task
@roles('ws')
def remove_jormungandr_instance(instance):
    #DEPRECATED
    """Remove a jormungandr instance entirely
        * Remove ini file which declare the instance
        * Reload apache
    """
    run("rm --force %s/%s.ini" % (env.jormungandr_instances_dir, instance))

    for server in env.roledefs['ws']:
        print("→ server: {}".format(server))
        execute(reload_jormun_safe, server)
