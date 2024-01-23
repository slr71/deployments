# Ansible Playbooks

## Kubernetes

The [Kubernetes playbooks](kubernetes) can be used to prepare nodes for inclusion in a new or existing Kubernetes
cluster.

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

## NATS

The DE uses NATS in the backend to communicate between some services. By default, NATS is installed in clustered mode
with 5 nodes. You should be able to connect to any node to communicate with other services using NATS. The 
[NATS playbooks](nats) will install `helm` inside the cluster and use it to set up and run NATS.
