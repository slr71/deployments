Role Name
=========

Installs the OpenLDAP Server for the CyVerse Discovery Environment

Role Variables
--------------

| Variable      | Description                                      | Default           |
| ------------- | ------------------------------------------------ | ----------------- |
| dn_suffix     | The suffix to use for DNs in the LDAP directory. | dc=cyverse,dc=org |
| root_password | The password to use for the manager account.     | notprod           |

Use of the default role variable values is not recommended for production systems.

Example Playbook
----------------

``` yaml
- hosts: ldap
  roles:
     - role: de-slapd
       vars:
         dn_suffix: dc=example,dc=org
         root_password: notreal
```

License
-------

BSD - https://www.cyverse.org/license
