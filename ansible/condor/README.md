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
timezone: UTC
docker:
  tag: "latest"
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
