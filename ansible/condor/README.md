# Htcondor Deployment Playbooks

The playbooks in this directory can be used to prepare to add a worker node to the HTCondor cluster for the CyVerse
Discovery Environment.

## Playbooks

### condor-exec-node.yml

This playbook installs HTCondor along with the software used by the CyVerse Discovery Environment to run jobs in
HTCondor.

### condor-exec-node-check.yml

This playbook performs a couple of tasks that can be useful for troubleshooting misbehaving HTCondor nodes in the
CyVerse Discovery Environment's HTCondor cluster:

- Restarts `iptables` and Docker in an attempt to fix a problem that can happen when `iptables` is restarted while
  Docker is running.
- Verifies that Docker is configured correctly to be able to pull images. The list of images to test can be specified in
  the group variables.

## Inventory Setup

```
[condor:children]
condor_worker
condor_submission
condor_manager

[condor_worker]
condor-node-1.example.org
condor-node-2.example.org

[condor_submission]
submission-node.example.org

[condor_manager]
central-manager-node.example.org
```

The groups are defined as follows:

| Group Name        | Description                                                 |
| ----------------- | ----------------------------------------------------------- |
| condor            | All condor nodes.                                           |
| condor_worker     | Condor worker nodes.                                        |
| condor_submission | This group contains the single Condor submission node.      |
| condor_manager    | This group contains the single Condor central manager node. |

The Condor submission group should consist of a single node from which all Condor jobs will be submitted. The workload
on this node can be relatively high, so it's generally a good idea for this node not to be used for anything other than
job submission.

The Condor central manager group should also consist of a single node that will manage the Condor cluster. In low
traffic environments, it may be useful for one of the worker nodes to double as a central-manager node, for example:

```
[condor:children]
condor_worker
condor_submission
condor_manager

[condor_worker]
condor-node-1.example.org
condor-node-2.example.org

[condor_submission]
submission-node.example.org

[condor_manager]
condor-node-1.example.org
```

## Group Variable Setup

``` yaml
environment_name: example
timezone: America/Phoenix
docker:
  tag: "latest"
  registry:
    base: "https://registry.example.org"
docker_registries:
  - host: registry.example.org
    user: "someuser"
    password: "notreal"
    test_image: "registry.example.org/image:latest"
condor:
  admin: "admin@example.org"
  uid_domain: "example.org"
  filesystem_domain: "example.org"
  collector_name: "example-collector"
  allow_read: [ "*.example.org", "1.2.3.0/24" ]
  allow_write: [ "*.example.org", "1.2.3.0/24" ]
  exec_dir: "/var/lib/condor/execute"
  password: "notreal"
```

| Variable Name                   | Description                                                                 |
| ------------------------------- | --------------------------------------------------------------------------- |
| environment_name                | The name of the DE deployment environment.                                  |
| timezone                        | The time zone to set for each of the Condor worker nodes.                   |
| docker.tag                      | The Docker tag to use when pulling images used to install CyVerse services. |
| docker.registry.base            | The base URL for the registry to use when pulling CyVerse Docker images.    |
| docker_registries               | A list of Docker registries for each Condor node to be authenticated with.  |
| docker_registries[n].host       | The host name for the Docker registry.                                      |
| docker_registries[n].user       | The username to use to authenticate to the Docker registry.                 |
| docker_registries[n].password   | The password to use to authenticate to the Docker registry.                 |
| docker_registries[n].test_image | A docker image that can be pulled to verify the authentication credentials. |
| condor.admin                    | The email address of the HTCondor administrator.                            |
| condor.uid_domain               | The user ID domain to use for HTCondor, which can be arbitrary.             |
| condor.filesystem_domain        | The file system domain to use for HtCondor, which can be arbitrary.         |
| condor.collector_name           | The name of the HTCondor collector, which can be arbitrary.                 |
| condor.allow_read               | See `ALLOW_READ` in the [HTCondor Authorization Documentation][1].          |
| condor.allow_write              | See `ALLOW_WRITE` in the [HTCondor Authorization Documentation][1].         |
| condor.exec_dir                 | The base directory where HTCondor jobs will run.                            |
| condor.password                 | The password required for nodes to join the HTCondor cluster.               |

[1]: https://htcondor.readthedocs.io/en/latest/admin-manual/security.html#authorization
