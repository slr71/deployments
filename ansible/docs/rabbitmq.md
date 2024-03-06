# RabbitMQ deployment/configuration playbooks

These playbooks can be used to install and/or configure RabbitMQ for usage by the DE services.

## Playbooks

### main.yml

This playbook both installs and configures RabbitMQ.

### configure.yml

This playbook only configures RabbitMQ, and is intended for use when the RabbitMQ host is installed separately, for example when iRODS and the DE share a broker.

## Inventory Setup

```
[amqp-brokers]
rabbitmq-host.example.org
```

The amqp-brokers group should include the host to install and/or configure RabbitMQ on.

## Group Variable Setup

The installation portion of these playbooks depends on the `amqp.admin_user` and `amqp.admin_password` variables. The configuration section depends on `amqp.de` and `amqp.irods`, which are definitions of vhosts.
