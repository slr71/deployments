# Ansible Playbooks

## Kubernetes

The [Kubernetes playbooks](kubernetes) can be used to prepare nodes for inclusion in a new or existing Kubernetes
cluster.

## OpenLDAP

The DE uses OpenLDAP using an RFC2307 schema as its user directory by default. If you don't have an existing LDAP
directory, the [OpenLDAP playbooks](ldap) can be used to create a new one. Note: the DE has not been tested with other
LDAP schemas.
