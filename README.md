Fabric
======

This file must be executed via python fabric, you can list all *tasks* by:

    fab --list

Or see list of all available tasks [here](tasks.md).

The configuration is done by calling a first configuration task which set all the needed parameters in the fabric's ```env``` variable.

If your configuration is outside of this repository (and it should!), you can add it in the python path and call the ```use``` task with the task you want to import.

ex:
    ```PYTHONPATH=~/dev/navitia_deployment_conf/ fab use:dev.dev deploy_from_scratch```

if you want to give extra parameters to the configuration task, add them after it's name:

    ```PYTHONPATH=~/dev/navitia_deployment_conf/ fab use:simple_one.simple_one,git@172.17.0.2 deploy_from_scratch```

Features:

* Setup a server from scratch:

    ```fab <conf> deploy_from_scratch```

* Upgrade the version of navitia:

    ```fab <conf> upgrade_all```

* Complete creation of an instance:
     for that you just need to call the setup of all instances, the remaining instances will just have their configuration updated

    ```fab <conf> update_all_instances```

* Complete removal of an instance on all components:

    ```fab dev remove_instance:fr-idf```

* Do the upgrade on the dev environnment:

Note: Special case to use for prod, disable ws1 and eng1 before

    fab dev prepare_upgrade
    fab dev upgrade_tyr
    fab dev launch_rebinarization_upgrade # long time to wait !
    fab dev upgrade_kraken
    fab dev upgrade_jormungandr
    
Note : you can use the variable env.nb_thread_for_bina in the definition of the environment to parallelize binarizations.

prod only, use ws1 and eng1

    fab prod use_upgraded_version
    
prod only, upgrade other ws and eng when prod validated

    fab prod upgrade_prod2

