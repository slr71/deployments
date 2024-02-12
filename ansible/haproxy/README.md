# HAProxy deployment playbooks

These playbooks can be used to install and configure HAProxy to serve as a reverse proxy for DE-related services including the UI.

## Playbooks

### main.yml

This playbook installs and configures HAProxy to forward traffic to the DE. This does not install the SSL certificates; for that use the `tls-certs` playbooks instead, whose folder should be a directory above this README.

## Inventory Setup

```
[de_proxy]
proxy-node.example.org

[k8s_de_workers]
k8s-node-1.example.org
k8s-node-2.example.org
```

The `de_proxy` group should contain the server set up as the proxy node. DNS for the environment's main access point should point to this server. The `k8s_de_workers` node should be set up as for the kubernetes roles, and should contain the nodes on which the DE might be running (nodes that will have the appropriate NodePorts set up to proxy to).

## Group Variable Setup

This playbook only needs one group variable, to set the external DNS name that should forward to Sonora, under the name `external_dns_name`.
