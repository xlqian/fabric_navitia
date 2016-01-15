from fabric.api import env
from fabfile.instance import add_instance
import common


def simple_one(addr_server_ed, addr_server_kraken=None):
    """
    Configuration simple example.

    All is installed on 2 servers:
    * one for the data integration (addr_server_ed)
    * one for the rest addr_server_kraken

    If addr_server_kraken is not provided, all is installed on addr_server_ed

    the address must be ssh formated addresses like my_user@my_server
    """
    env.use_ssh_config = True
    env.name = 'simple'
    env.distrib = 'debian8'

    if not addr_server_kraken:
        addr_server_kraken = addr_server_ed

    env.use_syslog = False

    env.postgresql_database_host = addr_server_ed
    env.roledefs = {
        'tyr':  [addr_server_ed],
        'tyr_master': [addr_server_ed],
        'db':   [addr_server_ed],
        'eng':  [addr_server_kraken],
        'ws':   [addr_server_kraken],
    }

    env.jormungandr_url = addr_server_kraken.split('@')[-1]
    env.setup_apache = True
    env.jormungandr_save_stats = False
    env.jormungandr_is_public = True
    env.tyr_url = 'localhost:6000'

    # with this, the navitia packages are handled as file copied to the server and installed with `dpkg -i`
    env.manual_package_deploy = True

    env.kill_ghost_tyr_worker = True
    env.dry_run = False
    env.nb_thread_for_bina = 2

    add_instance('paris', 'moovit_paris')

