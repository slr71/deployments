# Htcondor Deployment Playbooks

The playbooks in this directory can be used to install a Condor cluster and prepare it for use with the CyVerse
Discovery Environment.

## Playbooks

### install.yml

This playbook installs HTCondor along with the software used by the CyVerse Discovery Environment to run jobs in
HTCondor. The following software packages are installed:

- Python 3 and Pip (required for Ansible).
- Python 3 Docker client library (required for installing and configuring Docker).
- Docker
- HTCondor
- road-runner
- de-docker-logging-plugin
- de-image-janitor
- de-network-pruner

This playbook can also optionally log into docker registries.

## Inventory Setup

```
[condor:children]
condor_manager
condor_submit
condor_worker

[condor_manager]
central-manager-node.example.org

[condor_submit]
submit-node.example.org

[condor_worker]
condor-node-1.example.org
condor-node-2.example.org
```

 The groups are defined as follows:

| Group Name     | Description                                                 |
| -------------- | ----------------------------------------------------------- |
| condor         | All condor nodes.                                           |
| condor_manager | This group contains the single Condor central manager node. |
| condor_submit  | This group contains the single Condor submission node.      |
| condor_worker  | Condor worker nodes.                                        |

The Condor submit node group should consist of a single node from which all Condor jobs will be submitted. The workload
on this node can be relatively high, so it's generally a good idea for this node not to be used for anything other than
job submission.

The Condor central manager group should also consist of a single node that will manage the Condor cluster. In low
traffic environments, it may be useful for one of the worker nodes to double as a central-manager node, for example:

```
[condor:children]
condor_manager
condor_submit
condor_worker

[condor_manager]
condor-node-1.example.org

[condor_submit]
submit-node.example.org

[condor_worker]
condor-node-1.example.org
condor-node-2.example.org
```

## Group Variable Setup

``` yaml
---
timezone: "America/Phoenix"

condor_uid_domain: example.org
condor_pool_password: notreal
de_docker_logging_plugin_tag: latest
image_janitor_version: v3.0.0-rc04
network_pruner_version: v3.0.0-rc01
road_runner_version: v3.0.0
porklock_tag: dev

docker_registries:
  - host: "harbor.example.org"
    user: "robot$example"
    password: "stillnotreal"
    test_image: "harbor.example.org/hub/busybox:latest"
  - host: "https://index.docker.io/v1/"
    user: "example"
    password: "andyouthoughtthiswouldbereal"
    test_image: "busybox:latest"
```

| Variable Name                   | Description                                                                 |
| ------------------------------- | --------------------------------------------------------------------------- |
| timezone                        | The time zone to set for each of the Condor worker nodes.                   |
| condor_version                  | The version of HTCondor to install (optional).                              |
| condor_uid_domain               | The user ID domain to use for HTCondor, which can be arbitrary.             |
| condor_pool_password            | The password required for nodes to join the HTCondor cluster.               |
| de_docker_logging_tag           | The Docker image tag to use for the DE Docker logging plugin.               |
| image_janitor_version           | The version of `image-janitor` to install.                                  |
| network_pruner_version          | The version of `network-pruner` to install.                                 |
| road_runner_version             | The version of `road-runner` to install.                                    |
| porklock_tag                    | The Docker image tag to use for Porklock.                                   |
| docker_registries               | A list of Docker registries for each Condor node to be authenticated with.  |
| docker_registries[n].host       | The host name for the Docker registry.                                      |
| docker_registries[n].user       | The username to use to authenticate to the Docker registry.                 |
| docker_registries[n].password   | The password to use to authenticate to the Docker registry.                 |
| docker_registries[n].test_image | A docker image that can be pulled to verify the authentication credentials. |

[1]: https://htcondor.readthedocs.io/en/latest/admin-manual/security.html#authorization
