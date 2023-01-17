# HTCondor Deployment Playbooks

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
[condor]
condor-node-1.example.org
condor-node-2.example.org

[condor-submission]
submission-node.example.org

[condor-controller]
controller-node.example.org
```

The groups are defined as follows:

| Group Name        | Description                                            |
| ----------------- | ------------------------------------------------------ |
| condor            | All condor worker nodes.                               |
| condor-submission | This group contains the single Condor submission node. |
| condor-controller | This group contains the single Condor controller node. |

The Condor submission group should consist of a single node from which all Condor jobs will be submitted. The workload
on this node can be relatively high, so it's generally a good idea for this node not to be used for anything other than
job submission.

The Condor controller group should also consist of a single node that will manage the Condor cluster. In low traffic
environments, it may be useful for one of the worker nodes to double as a controller node, for example:

```
[condor]
condor-node-1.example.org
condor-node-2.example.org

[condor-submission]
submission-node.example.org

[condor-controller]
controller-node.example.org
```

## Group Variable Setup

```
timezone: UTC
```
