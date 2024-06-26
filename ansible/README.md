# Ansible Playbooks

## Required Ansible Collections

- community.general
- kubernetes.core
- community.crypto

## Database Initialization

The following databases are created by the `postgresql_init.yml` playbook:

| Database      | Owner    | Auto Init    | Auto Migrate |
| ------------- | -------- | ------------ | ------------ |
| de            | de       | no           | no           |
| notifications | de       | no           | no           |
| metadata      | de       | no           | no           |
| de_releases   | de       | no           | no           |
| grouper       | grouper  | yes          | ?            |
| qms           | de       | configurable | configurable |
| unleash       | de       | yes          | ?            |
| k3s           | de       | yes          | ?            |
| keycloak      | keycloak | yes          | ?            |

The owner users are configurable through the `dbms_connection_user` and `grouper_connection_user` group_vars.

Migrations are run for the `de`, `metadata`, `notifications`, and `de_releases` databases. The `k3s` database is initialized by the installation process for the k3s cluster and the `grouper` database is handled by its own playbook since it's fairly complicated. The `qms`
database is created here, but populated by the `qms` service. `unleash` is not yet initialized by this playbook.

| Playbook            | Description                                    | Example                                               |
| ------------------- | ---------------------------------------------- | ----------------------------------------------------- |
| postgresql_init.yml | Creates the databases and runs some migrations | `ansible-playbook -i <inventory> postgresql_init.yml` |

## Kubernetes

The [Kubernetes playbooks](kubernetes) can be used to prepare nodes for inclusion in a new or existing Kubernetes
cluster.

| Playbook                          | Description                        | Example                                                             |
| --------------------------------- | ---------------------------------- | ------------------------------------------------------------------- |
| kubernetes_uninstall_k8s.yml      | Uninstalls an existing k8s cluster | `ansible-playbook -i <inventory> -K kubernetes_uninstall_k8s.yml`   |
| kubernetes_setup_haproxy.yml      | Installs k3s reverse proxy         | `ansible-playbook -i <inventory> -K kubernetes_setup_haproxy.yml`   |
| kubernetes_install_k3s.yml        | Installs k3s                       | `ansible-playbook -i <inventory> -K kubernetes.yml`                 |
| kubernetes_de_reqs.yml            | Installs DE requirements           | `ansible-playbook -i <inventory> kubernetes_de_reqs.yml`            |
| kubernetes_install_csi_driver.yml | Installs the IRODS CSI driver      | `ansible-playbook -i <inventory> kubernetes_install_csi_driver.yml` |

## OpenLDAP

The DE uses OpenLDAP using an RFC2307 schema as its user directory by default. If you don't have an existing LDAP
directory, the [OpenLDAP playbooks](ldap) can be used to create a new one. Note: the DE has not been tested with other
LDAP schemas.

## RabbitMQ

The DE and CyVerse Data Store both use RabbitMQ as a message bus. The DE uses it for notifications, and the data store
uses it to push updates to ElasticSearch for indexing. The [RabbitMQ playbooks](rabbitmq) will install RabbitMQ on a
single node.

## HTCondor

The DE uses HTCondor to run non-interactive analyses. Several DE specific components are required for this to work, so
the recommended approach is to create a new HTCondor cluster that is dedicated to the DE. This can be done using the
[HTCondor playbooks](condor).

## Cert-Manager

The DE uses cert-manager to generate and rotate self-signed TLS certs for use with NATS. The following playbooks are available:

| Playbook         | Description           | Example                                            |
| ---------------- | --------------------- | -------------------------------------------------- |
| cert-manager.yml | Installs cert-manager | `ansible-playbook -i <inventory> cert_manager.yml` |

## NATS

The DE uses NATS in the backend to communicate between some services. By default, NATS is installed in clustered mode
with 5 nodes. You should be able to connect to any node to communicate with other services using NATS. The
[NATS playbooks](nats) will install `helm` inside the cluster and use it to set up and run NATS.

**NOTE** Make sure the `KUBECONFIG` environment variable is set to the correct value in your local shell.

| Playbook | Description   | Example                                    |
| -------- | ------------- | ------------------------------------------ |
| nats.yml | Installs NATS | `ansible-playbook -i <inventory> nats.yml` |

## GoCD

We use GoCD for continuous deployment. It's deployed outside of a kubernetes cluster to simplify the automation of cluster maintainance.

| Playbook            | Description                               | Example                                         |
| ------------------- | ----------------------------------------- | ----------------------------------------------- |
| gocd.yml            | Installs GoCD cluster                     | `ansible-playbook -i <inventory> -K gocd.yml`   |
| gocd_k3s_config.yml | Installs kubeconfig onto GoCD agent nodes | `ansible -i <inventory> -K gocd_k3s_config.yml` |

## Grouper

Grouper is installed inside the same cluster as the Discovery Environment, but the process is different enough from the rest of the services that it needs its own playbook and roles.

| Playbook    | Description                           | Example                                       |
| ----------- | ------------------------------------- | --------------------------------------------- |
| grouper.yml | Installs Grouper into the k3s cluster | `ansible-playbook -i <inventory> grouper.yml` |

## Keycloak

Keycloak is used for authentication/authorization and is installed inside the same cluster as the Discovery Environment.

| Playbook     | Description                            | Example                                        |
| ------------ | -------------------------------------- | ---------------------------------------------- |
| keycloak.yml | Installs keycloak into the k3s cluster | `ansible-playbook -i <inventory> keycloak.yml` |

## Services

The services playbook is used to install and upgrade the Discovery Environment services.

| Playbook            | Description             | Example                                                                        |
| ------------------- | ----------------------- | ------------------------------------------------------------------------------ |
| services_single.yml | Deploy a single service | `ansible-playbook -i <inventory> -e service=<service_name> single_service.yml` |
| services.yml        | Deploy all the services | `ansible-playbook -i <inventory> single.yml`                                   |
