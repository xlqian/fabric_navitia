Fabric_Navitia
==============
A set of fabric tasks to deploy, upgrade and manage Navitia2 platforms.

It is strongly tied to [navitia_deployment_conf](https://github.com/CanalTP/navitia_deployment_conf)
to deploy on CanalTP platforms.
Specific informations for deployment on CanalTP platforms are available on
[confluence DEVOPS page](http://confluence.canaltp.fr/pages/viewpage.action?spaceKey=DEVOPS&title=Navitia2),
you can also get some inspiration from `deploy_navitia_on_*` jobs on Jenkins platform.

TL;DR:
------
The main functions availables are in fabfile/tasks.py
Before any use a `pip install -r requirements.txt -U` is advised.

Main feature examples:

* Setup a server from scratch:

    ```PYTHONPATH=.:../navitia_deployment_conf/ fab use:dev deploy_from_scratch```

* Upgrade the version of navitia:

    ```PYTHONPATH=.:../navitia_deployment_conf/ fab use:dev upgrade_all```


Tasks
-----
You can list all available tasks by:

    fab --list

**WARNING:** When a task appears multiple times in that list, always use the namespaced ones.
When you have `deploy`, `kraken.deploy` and `jormungandr.deploy`,
there is no way to know for sure what `deploy` refers to.

General fabric command format (see below for pseudo-tasks):

    PYTHONPATH=<path_to_fabric_navitia>:<path_to_configuration> python -u -m fabric --keepalive=20 pseudo-task1:params pseudo-task2:params task1:params task2:params ... taskn:params

equivalent to

    PYTHONPATH=<path_to_fabric_navitia>:<path_to_configuration> fab --keepalive=20 pseudo-task1:params pseudo-task2:params task1:params task2:params ... taskn:params

The keepalive specifies an SSH keepalive interval.
See http://docs.fabfile.org/en/1.11/usage/fab.html for other parameters of fabric command line.

There are 3 tasks catagories:

 1. Deploy & upgrade,
 2. Management,
 3. Pseudo-tasks

Pseudo-tasks are not really tasks as their perform no action on the target platform.
Pseudo tasks are for configuration of real tasks.
Examples of pseudo-tasks are: "use" to select the target platform, "include" to select the set of coverages.

Task parameters are joined to task name after a colon (:)
1- Positional parameters = list of words separated by periods (no space).

    task:param1,param2,...,paramn

2- Named parameters = list of "word=value"  separated by periods (no space).

    task:param1=value1,param2=value2,...,paramn=valuen

Mixing parameters types is possible as of python rules, i.e. positional parameters first, then named parameters.

Pseudo-tasks
------------
**use**: Select a target platform.
Will load and execute a configuration from a platform file in a configuration folder. Ex:

    PYTHONPATH=<path_to_fabric_navitia>:<path_to_configuration> fab use:prod

Will load python module prod.py from "path_to_configuration" and run function prod().

**include**: Select a set of coverages.
Will reduce the set of active coverages to the list of given positional paramters. Ex:

    PYTHONPATH=<path_to_fabric_navitia>:<path_to_configuration> fab use:<platform> include:fr-idf,fr-lyon,us-ny,nz task

Will run the fabric task on this reduced set of coverages.
Nota: specified coverages must be among the active coverages of the target platform.

**exclude**: Remove coverages from the active coverage set. Ex:

    PYTHONPATH=<path_to_fabric_navitia>:<path_to_configuration> fab use:<platform> exclude:fr-idf,fr-lyon,us-ny,nz task

Will run the fabric task on the active set of coverages minus these specified coverages.
Nota: specified coverages must be among the active coverages of the target platform.

**set**: force an api.env attribute value.

Deploy & Upgrade
----------------

**deploy_from_scratch**: (no params) deploy a fresh navitia2 on a new platform.

**upgrade_all**: deploy an upgrade of navitia2.
This is the most complex task of fabric_navitia. It completely automates the upgrade process, which consists of:

 1. upgrade all navitia packages,
 2. migrate databases,
 3. launch rebinarization of all coverages,
 4. restart krakens and jormungandr,
 5. redeploy configurations (tyr, kraken, jormungandr),
 6. optionally, send mail at start and end of process

This task has 7 named parameters:

| param                        |  Description |
|------------------------------|--------------|
| up_tyr (default=True)        |  If false, will skip the upgrade of tyr package, as well as all binarizations |
| up_confs (default=True)      |  If false, will skip the redeployment of configurations. Can save time if you know for sure that conf is not changed |
| kraken_wait (default=True)   |  Wait when restarting krakens |
| check_version (default=True) |  Check packages version before upgrading |
| send_mail (default='no')     |  Controls mail broadcast. Other values are 'start', 'end', 'all'|
| manual_lb (default=False)    |  Switch load balancers control method (for prod only) |
| check_dead (default=True)    | Controls wether dead_instances threshold is applied or not |

**update_tyr_step**: deploy an upgrade of tyr:

 1. upgrade tyr package,
 2. migrate databases,
 3. launch rebinarization of all coverages,

**update_jormungandr_conf**: deploys jormungandr configuration. Needs a restart_jormungandr to activate the configuration (see below).

**update_all_configurations**: redeploy all configurations (tyr, jormun, coverages) and restarts all services (tyr, kraken, jormun).

**update_instance**:  deploy a new coverage or deploy it again. (param=coverage name).


Management
----------
Some important management tasks:

**restart_kraken**: restart all krakens on all servers. Seldom used.

**restart_jormungandr**: restart jormungandr on all servers. Use to resynchronize jormun vs krakens or to activate new jormun configuration.

**launch_rebinarization**: launch a binarization on a single coverage, based on last dataset. (param=coverage name).

**launch_rebinarization_upgrade**: launch a migration (upgrade) of ed database and a binarization on all coverages, with a controlled level of parallelization.

Note : you can use the variable env.nb_thread_for_bina in the definition of the environment to parallelize binarizations.
