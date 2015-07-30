Available commands:

    alpha
    artemis
    create_instance                                       Create a new navitia2 PRIVATE instance
    create_kraken_vip                                     Create a F5 VS and a same name pool for a given port
    customer
    dev
    exploit                                               Exploitation test env @EQX
    install_pip_requirements                              For installing requirements, give a role as argument
    internal
    let                                                   This function is a way to give env variables in the cli
    pre
    prepare_upgrade                                       Backup data.nav.lz4, check dataset existence, etc...
    prod
    really_run                                            If called set dry_run as false
    remove_instance                                       Completely remove all components for a given instance
    remove_kraken_vip                                     Delete a given instance vip and associated pool
    rename_instance                                       Rename a given instance with new name
    rollback_upgraded_version                             Prod only: use previous version components in lb
    sim
    update_all_ed_databases_to_alembic                    Migrate ED database handled by bash scripts to alembic.
    upgrade_all                                           Upgrade all navitia packages, databases and launch rebinarisation of all instances
    upgrade_all_packages                                  Upgrade all navitia packages
    upgrade_jormungandr                                   Upgrade and restart all jormun instances
    upgrade_kraken                                        Upgrade and restart all kraken instances
    upgrade_tyr                                           Upgrade all ed instances db, launch bina
    upgrade_version                                       install a new version and update databases.
    use_monitor_kraken_healthcheck                        Use monitor-kraken instead of tcp
    use_tcp_healthcheck                                   Use tcp monitor instead of monior_kraken
    use_upgraded_version                                  Prod only: use ws1 and eng1 instead of ws2, eng{2,4}
    custom_tasks.update_all_ed_databases_to_alembic       Migrate ED database handled by bash scripts to alembic.
    prod_tasks.create_kraken_vip                          Create a F5 VS and a same name pool for a given port
    prod_tasks.remove_kraken_vip                          Delete a given instance vip and associated pool
    prod_tasks.rollback_upgraded_version                  Prod only: use previous version components in lb
    prod_tasks.use_monitor_kraken_healthcheck             Use monitor-kraken instead of tcp
    prod_tasks.use_tcp_healthcheck                        Use tcp monitor instead of monior_kraken
    prod_tasks.use_upgraded_version                       Prod only: use ws1 and eng1 instead of ws2, eng{2,4}
    tasks.create_instance                                 Create a new navitia2 PRIVATE instance
    tasks.install_pip_requirements                        For installing requirements, give a role as argument
    tasks.launch_rebinarization_upgrade                   launch binarization on all instances for the upgrade
    tasks.prepare_upgrade                                 Backup data.nav.lz4, check dataset existence, etc...
    tasks.remove_instance                                 Completely remove all components for a given instance
    tasks.rename_instance                                 Rename a given instance with new name
    tasks.upgrade_all                                     Upgrade all navitia packages, databases and launch rebinarisation of all instances
    tasks.upgrade_all_packages                            Upgrade all navitia packages
    tasks.upgrade_jormungandr                             Upgrade and restart all jormun instances
    tasks.upgrade_kraken                                  Upgrade and restart all kraken instances
    tasks.upgrade_tyr                                     Upgrade all ed instances db, launch bina
    tasks.upgrade_version                                 install a new version and update databases.
    tasks.db.call_tyr_http_authorization
    tasks.db.check_is_postgresql_user_exist               Check if a given postgresql user exist
    tasks.db.create_postgresql_database                   Create a postgresql database
    tasks.db.create_postgresql_user                       Create a postgresql user
    tasks.db.postgis_initdb                               Populate the a database with postgis
    tasks.db.remove_ed_database                           Remove a given ed instance in jormungandr PostgreSQL db
    tasks.db.remove_postgresql_database                   Remove a postgresql database
    tasks.db.remove_postgresql_user                       Create a postgresql user
    tasks.db.rename_postgresql_database                   Rename a postgresql database and the SAME corresponding username
    tasks.db.rename_tyr_jormungandr_database              Rename the instance id in the jormungandr database
    tasks.db.set_instance_authorization
    tasks.db.set_tyr_is_free                              Set is_free flag in jormungandr database for a given instance
    tasks.jormungandr.create_jormungandr_instance         Create a jormungandr instance
    tasks.jormungandr.get_jormungandr_config              Get jormungandr configuration of a given instance
    tasks.jormungandr.remove_jormungandr_instance         Remove a jormungandr instance entirely
    tasks.jormungandr.restart_jormungandr                 Used to restart jormungandr on a given server
    tasks.jormungandr.restart_jormungandr_all             Restart jormungadr on all servers
    tasks.jormungandr.set_jormungandr_config              Use the given kraken in the jormungandr server
    tasks.jormungandr.test_jormungandr                    Test jormungandr globally (/v1/coverage) or a given instance
    tasks.jormungandr.upgrade_ws_packages
    tasks.jormungandr.kraken.create_eng_instance          Create a new kraken instance
    tasks.jormungandr.kraken.disable_rabbitmq_kraken      Disable kraken rabbitmq connection through iptables
    tasks.jormungandr.kraken.disable_rabbitmq_standalone  Disable rabbitmq via network or by changing tyr configuration
    tasks.jormungandr.kraken.enable_rabbitmq_kraken       Enable kraken rabbitmq connection through iptables
    tasks.jormungandr.kraken.enable_rabbitmq_standalone   Enable rabbitmq via network or by changing tyr configuration
    tasks.jormungandr.kraken.get_kraken_config            Get kraken configuration of a given instance
    tasks.jormungandr.kraken.get_kraken_instances         Return the list of kraken instances
    tasks.jormungandr.kraken.get_no_data_instances        Get instances that have no data loaded ("status": null)
    tasks.jormungandr.kraken.remove_kraken_instance       Remove a kraken instance entirely
    tasks.jormungandr.kraken.rename_kraken_instance       Rename a kraken instance
    tasks.jormungandr.kraken.restart_all_kraken           Restart all kraken instances on a given server
    tasks.jormungandr.kraken.restart_kraken               Restart a kraken instance on a given server
    tasks.jormungandr.kraken.test_all_kraken              Test all kraken instances on a given server
    tasks.jormungandr.kraken.test_kraken                  Test kraken with '/monitor-kraken/?instance='
    tasks.jormungandr.kraken.upgrade_engine_packages
    tasks.load_balancer.disable_node                      Disable F5 ADC node
    tasks.load_balancer.enable_node                       Enable F5 ADC node
    tasks.realtime.restart_sindri                         Restart each sindri instances
    tasks.tyr.backup_datanav                              Backup a data.nav.lz4 for a given instance in data.nav.lz4_$instance
    tasks.tyr.create_tyr_instance                         Create a *private* tyr instance based on the given name
    tasks.tyr.get_ed_instances                            Return the list of ed instances
    tasks.tyr.get_instance_id                             Return the id of a given instance
    tasks.tyr.get_kraken_config                           Get kraken configuration of a given instance
    tasks.tyr.get_kraken_instances                        Return the list of kraken instances
    tasks.tyr.get_no_data_instances                       Get instances that have no data loaded ("status": null)
    tasks.tyr.get_tyr_config                              Get tyr configuration of a given instance
    tasks.tyr.get_tyr_last_done_job_id                    Return the last done job for an instance
    tasks.tyr.get_tyr_last_pt_data_set                    Return the data_set used for
    tasks.tyr.launch_rebinarization_upgrade               launch binarization on all instances for the upgrade
    tasks.tyr.launch_rebinarization                       Re-launch binarization of previously processed input data
    tasks.tyr.remove_at_instance                          Remove an at / connector_rt instance entirely
    tasks.tyr.remove_ed_instance                          Remove a ed instance entirely
    tasks.tyr.remove_sindri_instance                      Remove a tyr instance entirely
    tasks.tyr.remove_tyr_instance                         Remove a tyr instance entirely
    tasks.tyr.rename_tyr_instance
    tasks.tyr.restart_tyr_reloader
    tasks.tyr.restart_tyr_worker
    tasks.tyr.rollback_datanav                            Rollback a data.nav.lz4_$instance file for a given instance
    tasks.tyr.start_tyr_beat
    tasks.tyr.start_tyr_reloader
    tasks.tyr.start_tyr_worker
    tasks.tyr.stop_tyr_beat
    tasks.tyr.stop_tyr_worker
    tasks.tyr.test_tyr_backup_file_presence               Test if there is a binarization job done and corresponding input file exist
    tasks.tyr.tyr_beat_status
    tasks.tyr.tyr_reloader_status
    tasks.tyr.update_ed_db                                upgrade the instance database schema
    tasks.tyr.update_jormungandr_db                       Update jormungandr database
    tasks.tyr.upgrade_ed_packages
    tasks.tyr.upgrade_tyr_packages
    tasks.tyr.verify_tyr_dest_dir_exists                  Verify that the dest dir of all instances exists
    tasks.utils.start_puppet
    tasks.utils.stop_puppet

