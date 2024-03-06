# TLS Certificate Deployment playbooks

This playbook is for copying TLS certificates to hosts.

## Playbooks

### main.yml

Copies TLS certs to appropriate nodes.

## Inventory Setup

```
[de_proxy]
proxy-node.example.org
```

These inventories should match other playbooks used for deployment.

## Variable setup

This playbook needs one variable, which most likely should be passed on the command line and not included in group vars: `combined_cert_src` should point to the `cyverse.combined` certificate to be used by HAProxy.

## Example

```
ansible-playbook -i /home/user/inventory-repo/inventory/ -e combined_cert_src=/home/user/certificates-source/ssl/cyverse.combined -K main.yml
```
