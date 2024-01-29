# Kubernetes Deployment Playbooks

The playbooks in this directory can be used to create a Kubernetes cluster for use with the CyVerse Discovery
Environment.

## Playbooks

### install.yml

This playbook prepares nodes for running Kubernetes:

- Installs and configures haproxy for the node running the load balancer for the Kubernetes API.
- Configures the firewall for use with Kubernetes.
- Installs and starts docker.
- Installs kubeadm, kubectl, and kubelet.
- Starts kubelet.

### create.yml

This playbook creates the Kubernetes cluster:

- Initializes the cluster on the first node listed in the `k8s-controllers` group.
- Joins the remaning nodes in the `k8s_controllers` group.
- Joins the nodes in the `k8s_workers` group, which is comprised of the `k8s_de_workers`, `k8s_vice_workers`, and
  `k8s_gpu_workers` groups.
- Labels the nodes in the `k8s_de_workers` group.
- Taints and labels the nodes in the `k8s_vice_workers` group.
- Taints and labels the nodes in the `k8s_gpu_workers` group.

## Inventory Setup

The inventory for these playbooks is relatively simple:

```
[k8s:children]
k8s_nodes
k8s_api_proxy

[k8s_nodes:children]
k8s_controllers
k8s_workers

[k8s_workers:children]
k8s_de_workers
k8s_vice_workers
k8s_gpu_workers

[k8s_api_proxy]
k8s-haproxy.example.org

[k8s_controllers]
k8s-con-1.example.org
k8s-con-2.example.org
k8s-con-3.example.org

[k8s_de_workers]
k8s-worker-1.example.org
k8s-worker-2.example.org
k8s-worker-3.example.org
k8s-worker-4.example.org
k8s-worker-5.example.org
k8s-worker-6.example.org
k8s-worker-7.example.org

[k8s_vice_workers]
k8s-vice-1.example.org
k8s-vice-2.example.org
k8s-vice-3.example.org
k8s-vice-4.example.org

[k8s_gpu_workers]
k8s-gpu-1.example.org
k8s-gpu-2.example.org
k8s-gpu-3.example.org
k8s-gpu-4.example.org
```

The `k8s_api_proxy` group contains just a single node, which runs `haproxy` to act as a load balancer between all of the
Kubernetes worker nodes. In clusters that have only one controller node, The controller node itself can act as the
reverse proxy. In clusters with multiple controller nodes, it's highly recommended to have a dedicated node for the
reverse proxy.

The `k8s_controllers` group contains the Kubernetes control nodes.

The `k8s_worker` group contains all of the workder nodes in the cluster, including VICE worker nodes.

The `k8s_de_workers` group contains the Kubernetes worker nodes reserved for running CyVerse Discovery Environment
Services.

The `k8s_vice_workers` group contains all of the Kubernetes worker nodes reserved for running VICE apps that do not
require GPU access.

The `k8s_gpu_workers` group contains all of the Kubernetes worker nodes reserved for running VICE apps that require GPU
access.

## Group Variable Setup

No group variables are required for these playbooks at this time.

## Examples

Here are some examples to help get started.

### Prepare to Create the Cluster

```
$ ansible-playbook -i /path/to/inventory -K install.yml
```

### Create the Cluster

```
$ ansible-playbook -i /path/to/inventory -K create.yml
```
