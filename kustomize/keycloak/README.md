# Keycloak

The CyVerse Discovery Environment (DE) uses Keycloak as its primary authentication provider. In most cases, Keycloak is
deployed inside the Kubernetes cluster and made available via a load balancer or a node port.

## Database

This kustomization expects the DBMS to be available and accessible already. Most deployments use PostgreSQL, but other
database management systems should work as well. These instructions assume that you're using PostgreSQL.

### Create the Database User

For this example, we're going to assume that the databse username is Keycloak, although it doesn't have to be.

``` sql
postgres=> create user keycloak with password 'some-password';
CREATE ROLE
```

### Create the Database

This kustomization currently expects the database name to be `keycloak`, and these instructions assume that you're
logged into the DBMS as `postgres`. On more recent versions of Postgres, it's necessary to explicitly grant the role of
the account you're going to be using to the admin account that you're currently using. You can do that like this:

``` sql
postgres=> grant keycloak to postgres;
GRANT ROLE
```

The next step is to create the database itself.

``` sql
postgres=> create database keycloak with owner keycloak;
CREATE DATABASE
```

The public schema will still be owned by `postgres`, so it will be necessary to change its ownership as well. You can do
that like this:

``` sql
postgres=> \c keycloak
SSL connection (protocol: TLSv1.2, cipher: ECDHE-RSA-AES256-GCM-SHA384, bits: 256, compression: off)
You are now connected to database "keycloak" as user "postgres".

keycloak=> alter schema public owner to keycloak;
ALTER SCHEMA
```

## Secrets

Secrets are used to store sensitive information that should not be visible to most users. The secrets are created using
secret generators defined in `kustomization.yaml`, for example:

``` yaml
secretGenerator:
- name: dbuser
  behavior: merge
  literals:
  - username=keycloak
  - password=some-password
- name: kcadmin
  behavior: merge
  literals:
  - username=keycloak_admin
  - password=some-other-password
```

The first secret, `dbuser`, contains the username and password of the account used to access the database. The second
secret, `kcadmin`, contains the username and password of the Keycloak administrator account.

## ConfigMaps

ConfigMaps are used to store less sensitive information. The secrets are created using ConfigMap generators defined in
`kustomization.yaml`, the full definition in the base looks like this:

``` yaml
configMapGenerator:
- name: keycloak-config
  literals:
  - KEYCLOAK_HOSTNAME=keycloak.example.org
  - KEYCLOAK_LOGLEVEL=INFO
  - DB_VENDOR=postgres
  - DB_ADDR=postgres.example.org
  - DB_PORT=5432
  - PROXY_ADDRESS_FORWARDING=true
  - JDBC_PARAMS=connectTimeout=21600
  - JAVA_OPTS=-server
    -Xms4096m
    -Xmx8192m
    -XX:MetaspaceSize=96m
    -XX:MaxMetaspaceSize=256m
    -Djboss.modules.system.pkgs=org.jboss.byteman
    -Djava.awt.headless=true
    -Dkeycloak.profile.feature.token_exchange=enabled
    -Djava.security.egd=file:/dev/urandom
```

Most of the default settings can be left alone, but the settings that require host names or IP addresses will have to be
changed. You can specify custom configuration values in your own overlay like this:

``` yaml
configMapGenerator:
- name: keycloak-config
  behavior: merge
  literals:
  - KEYCLOAK_HOSTNAME=auth.example.org
  - DB_ADDR=db.example.org
```

Any of the configuration values in the base ConfigMap can be changed in this manner.

## Examples

A couple of examples are provided for reference.

The [AWS example](overlays/aws-example) configures the base overlay to create a service of type `LoadBalancer` and adds
annotations that will tell Amazon's Load Balancer Controller to create a load balancer with TLS termination. Your EKS
cluster needs to be configured to use the Load Balancer Controller before you can use a configuration like this. Please
see the [Load Balancer Controller User Guide][1] for more details.

The [Node Port Example](overlays/node-port-example) configures the base overlay to create a service of type `NodePort`
that listens on port 31360. This deployment style requires an external load balancer such as HAProxy or NGINX to be
deployed separately, with TLS termination enabled. Instructions for deploying the external load balancer are not
provided at this time.

[1]: https://docs.aws.amazon.com/eks/latest/userguide/aws-load-balancer-controller.html
