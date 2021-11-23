# Kubernetes Deployment Playbooks

The playbooks in this directory can be used to configure the firewall and install software in preparation for adding a
node to a Kubernetes cluster.

## Playbooks

### firewalld-config.yml

This playbook configures the firewall for Kubernets on nodes that use `firewalld`. The configuration contains four IP
sets:

| IP Set         | Description                                               |
| -------        | -----------                                               |
| overlay        | The CIDR block for the overlay network used by Kubernetes |
| haproxy        | The nodes where the HAproxy instances are running         |
| k8s-controller | The Kubernets controller nodes                            |
| k8s-worker     | The Kubernetes worker nodes                               |

The configuration also contains numerous service definitions:

| Service        | Description                                                       |
| -------        | -----------                                                       |
| cni-flannel    | Flannel overlay network                                           |
| cni-weavenet   | WeaveNet overlay network                                          |
| consul         | Consul                                                            |
| etcd           | Etcd, which is used internally by the Kubernetes controller nodes |
| kube-apiserver | The Kubernetes REST API                                           |
| kubelet-api-ro | The read-only port for the Kubelet API                            |
| kubelet-api-rw | The read/write port for the Kubelet API                           |
| node-ports     | A port range for Kubernetes services defining node ports          |
| vault          | Vault                                                             |

It also contains four custom zone definitions corresponding to the IP sets mentioned above:

| Zone           | Description                            |
| ----           | -----------                            |
| haproxy        | Nodes that will be running haproxy     |
| k8s-controller | Kubernetes controller nodes            |
| k8s-worker     | Kubernetes worker nodes                |
| overlay        | The overlay network used by kubernetes |

### provision-nodes.yml

This playbook provisions the nodes for the Kubernetes cluster. It performs the following tasks:

- Installs and configures haproxy for the node running the load balancer for the Kubernetes API.
- Installs and starts docker.
- Installs and starts kubelet.

Note: This playbook assumes that `iptables` is being used to manage the firewall directly. If `firewalld` is being used
then the `firewall` tag should be skipped.

### vice-haproxy-install.yml

This playbook provisions the reverse proxy instance used for VICE.

## Inventory Setup

The inventory for these playbooks is relatively simple:

```
[k8s:children]
k8s-control-plane
k8s-worker

[kube-apiserver-haproxy]
k8s-reverse-proxy.example.org

[k8s-control-plane]
k8s-controller-1.example.org
k8s-controller-2.example.org
k8s-controller-3.example.org

[k8s-storage:children]
k8s-worker

[k8s-worker]
k8s-worker-1.example.org
k8s-worker-2.example.org
k8s-worker-3.example.org
k8s-worker-4.example.org
k8s-worker-5.example.org
vice-worker-1.example.org
vice-worker-2.example.org
vice-worker-3.example.org

[outward-facing-proxy]
vice-haproxy.example.org

[haproxy]
vice-haproxy.example.org
other-haproxy-1.example.org
other-haprosy-2.example.org

[vice-workers]
vice-worker-1.example.org
vice-worker-2.example.org
vice-worker-3.example.org
```

The `kube-apiserver-haproxy` group contains just a single node, which runs `haproxy` to act as a load balancer between
all of the Kubernetes worker nodes. In clusters that have only one controller node, The controller node itself can act
as the reverse proxy. In clusters with multiple controller nodes, it's highly recommended to have a dedicated node for
the reverse proxy.

The `k8s-control-plane` group contains the Kubernetes control nodes.

The `k8s-worker` group contains all of the workder nodes in the cluster, including VICE workder nodes.

The `outward-facing-proxy` group contains the node running the reverse proxy used for VICE.

The `haproxy` group contains all of the haproxy nodes that are used to access services running inside Kubernetes,
including the one used for VICE. Except for the reverse proxy used for VICE (which is also in another group) these nodes
are not modified by any of these playbooks. Their IP addresses are used to configure firewalls, however.

The `vice-workers` group contains the Kubernetes worker nodes that will be dedicated to running VICE.

## Group Variable Setup

No group variables are required for these playbooks at this time.

## Adding a Worker Node to an Existing Cluster

### Configure the Firewall

This task only has to be performed separately if the firewall is not managed directly by `iptables`. If you are using
`iptables` directly, you can skip this step. If you're using `firewalld`, you can run the playbook to configure the
firewall:

```
$ ansible-playbook -i /path/to/inventory -K firewalld-config.yml
```

If you're using a different firewall then it will be necessary to configure it manually. The following ports should be
open:

| Service         | Ports       | Protocol | Accessibility                                                        |
| -------         | -----       | -------- | -------------                                                        |
| Flannel         | 6783        | TCP      | From all k8s nodes to all other k8s nodes.                           |
| WeaveNet        | 6783:6784   | UDP      | From all k8s nodes to all other k8s nodes.                           |
| Etcd            | 2379:2380   | TCP      | From all k8s controller nodes to all other controller nodes.         |
| Kube API Server | 5443        | TCP      | Between all k8s nodes and the k8s load balancer.                     |
| Kube API Server | 5443        | TCP      | From any node used for k8s administration and the k8s load balancer. |
| Kubelet API     | 10255,10250 | TCP      | Between all k8s nodes.                                               |
| Node Ports      | 30000:32767 | TCP      | Between all k8s nodes, and from all haproxy nodes to all k8s nodes.  |

### Provision the Nodes

```
$ ansible-playbook -i /path/to/inventory -K provision-nodes.yml \
    --limit=node1.example.org,node-2.example.org
```

### Generate a Token

Run this command on one of the existing controller nodes as root:

```
# kubeadm token create --print-join-command
```

The output should look something like this:

```
kubeadm join k8s-reverse-proxy.example.org:5443 \
    --token <join-token> \
    --discovery-token-ca-cert-hash <certificate-hash>
```

Keep a copy of that command available to run on the worker nodes that you're planning to add.

### Add the Workers to the Cluster

Run the `kubeadm join` command from the previous step as root. After running the command, read the output to verify that
the command finished successfully. If it did finish successfully, you can keep an eye on the Kubernetes logs by running
this command:

```
# journalctl -flu kubelet
```

It's also a good idea to run `kubectl get nodes` on any node that has access to the Kubernetes cluster in order to
determine whether or not the node becomes available.

### Tainting and Labeling VICE Worker Nodes

The CyVerse Discovery Environment uses taints and labels to ensure that some nodes are used exclusively for VICE
analyses. To mark a node as a VICE worker node, run this command on any node that has access to the Kubernetes API:

```
$ kubectl label nodes vice-worker-1.example.org vice=true
```

To prevent non-VICE pods from running on a node, run this command:

```
$ kubectl taint nodes vice-worker-1.example.org vice=only:NoSchedule
```
