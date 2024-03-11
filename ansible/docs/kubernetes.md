# Kubernetes Deployment Playbooks

The playbooks in this directory can be used to create a Kubernetes cluster for use with the CyVerse Discovery
Environment.

## Playbooks

### install_k3s.yml

Prepares nodes for running the k3s distribution of kubernetes:

- Installs wireguard on the nodes for use with the wireguard-native CSI driver.
- Configures the firewall for use with K3s.
- Sets up support for pulling images from the CyVerse image repo.
- Installs and runs the installation script for k3s.
- Joins nodes to the cluster.
- Labels and taints nodes for running DE services, VICE apps, and GPU-enabled VICE-apps.
- Installs the IRODS CSI driver.
- Sets up namespaces, service accounts, roles, role bindings, and cluster role bindings.

### install_csi_driver.yml

Installs the CSI driver into the k3s cluster. Also runs as part of the `install_k3s.yml` playbook.

### setup_haproxy.yml

Sets up the HAProxy in front of the K3s controllers. Runs as part of the `install_k3s.yml` playbook. Shouldn't need to be run manually, but it's here just in case.

### uninstall_k8s.yml

Uninstalls the current k8s cluster. Be very careful with this one, likely won't need to be run more than once internally and never for external deployments. Will probably be removed at some point in the future.

### update.yml

Runs updates on the k3s/k8s nodes. Likely will be moved elsewhere in the future.

## Inventory Setup

The inventory for these playbooks is relatively simple:

```
[k3s:children]
k3s_nodes
k3s_api_proxy

[k3s_nodes:children]
k3s_controllers
k3s_workers

[k3s_workers:children]
k3s_de_workers
k3s_vice_workers
k3s_gpu_workers

[k3s_api_proxy]
k3s-haproxy.example.org

[k3s_controllers]
k3s-con-1.example.org
k3s-con-2.example.org
k3s-con-3.example.org

[k3s_de_workers]
k3s-worker-1.example.org
k3s-worker-2.example.org
k3s-worker-3.example.org
k3s-worker-4.example.org
k3s-worker-5.example.org
k3s-worker-6.example.org
k3s-worker-7.example.org

[k3s_vice_workers]
k3s-vice-1.example.org
k3s-vice-2.example.org
k3s-vice-3.example.org
k3s-vice-4.example.org

[k3s_gpu_workers]
k3s-gpu-1.example.org
k3s-gpu-2.example.org
k3s-gpu-3.example.org
k3s-gpu-4.example.org
```

The `k3s_api_proxy` group contains just a single node, which runs `haproxy` to act as a load balancer between all of the
Kubernetes worker nodes. In clusters that have only one controller node, The controller node itself can act as the
reverse proxy. In clusters with multiple controller nodes, it's highly recommended to have a dedicated node for the
reverse proxy.

The `k3s_controllers` group contains the Kubernetes control nodes.

The `k3s_worker` group contains all of the workder nodes in the cluster, including VICE worker nodes.

The `k3s_de_workers` group contains the Kubernetes worker nodes reserved for running CyVerse Discovery Environment
Services.

The `k3s_vice_workers` group contains all of the Kubernetes worker nodes reserved for running VICE apps that do not
require GPU access.

The `k3s_gpu_workers` group contains all of the Kubernetes worker nodes reserved for running VICE apps that require GPU
access.

## Group Variable Setup

Default variables are definied in the `common` role, in the `roles/common/defaults/main.yml` file. Every other role defined for the k3s installation should depend on the common role.

Here are the default variables:

| Variable                                 | Default                                          | Override Required | Description                                              |
| ---------------------------------------- | ------------------------------------------------ | ----------------- | -------------------------------------------------------- |
| dbms_connection_user                     | de                                               | no                | The user k3s uses to connect to its database             |
| dbms_connection_pass                     | Ch@ng3M3                                         | yes               | The password k3s uses to connect to its database         |
| ns                                       | qa                                               | probably          | The namespace the DE services are installed into         |
| vice_ns                                  | vice-apps                                        | no                | The namespace the VICE apps run in                       |
| force_reinstall                          | false                                            | no                | Forces a reinstall of k3s                                |
| k3s_token                                | K3sT0k3n                                         | probably          | The token used to register nodes in the cluster          |
| k3s_version                              | v1.29.1+k3s1                                     | no                | The version of k3s to install                            |
| k3s_flannel_backend                      | wireguard-native                                 | no                | The flannel backend to use in k3s                        |
| k3s_registry_mirror                      | https://registry-1.docker.io                     | probably          | Image repo mirrored inside the cluster                   |
| k3s_registry_mirror_endpoint             | https://registry-1.docker.io                     | probably          | Mirrored image repo endpoint                             |
| k3s_registry_mirror_token:               |                                                  | yes               | Token used to connect to mirrored repo                   |
| k3s_registry_mirror_insecure_skip_verify | false                                            | no                | Enable TLS validation for mirrored repo                  |
| k3s_datastore_endpoint                   | postgres://de:password@example.org:5432/k3s      | yes               | PostgreSQL connection URL used by k3s                    |
| k3s_kubeconfig_output                    | "/etc/rancher/k3s/k3s.yaml"                      | no                | The path to the k3s kubeconfig for the cluster           |
| k3s_kubeconfig_mode                      | "644"                                            | no                | The file permissions for the generated kubeconfig file   |
| irods_csi_driver_repo                    | https://cyverse.github.io/irods-csi-driver-helm/ | no                | Helm repo location for the IRODS CSI driver              |
| irods_csi_driver_namespace               | irods-csi-driver                                 | no                | IRODS CSI driver installation namespace                  |
| irods_csi_driver_client                  | irodsfuse                                        | no                | Client type used by IRODS CSI driver                     |
| irods_csi_driver_host                    | data.cyverse.org                                 | probably          | Host connected to by IRODS CSI driver                    |
| irods_csi_driver_port                    | 1247                                             | no                | Port connected to by IRODS CSI driver                    |
| irods_csi_driver_zone                    | cyverse                                          | probably          | IRODS Zone used by IRODS CSI driver                      |
| irods_csi_driver_user                    | not_a_user                                       | yes               | Proxy User used by the IRODS CSI driver                  |
| irods_csi_driver_password                | not_a_password                                   | yes               | Proxy Password used by the IRODS CSI driver              |
| irods_csi_driver_retain_data             | "false"                                          | no                | Whether to cache data accessed through IRODS CSI driver  |
| irods_csi_driver_enforce_proxy_access    | "true"                                           | no                | Mandate using different user from global configuration   |
| irods_csi_driver_mount_path_white_list   | "/not/a/path"                                    | yes               | Comma-separate list of paths that can be mounted.        |
| irods_csi_driver_cache_size_max          | 10737418240                                      | no                | Maximum size of the cache maintained by IRODS CSI driver |
| irods_csi_driver_data_root               | "/irodsfs-pool"                                  | no                | IRODS mount path, with subdir per volume                 |

Additionally the `irods_csi_driver_cache_timeout_settings` takes a JSON encoded string that looks like the following:

```json
[
  { "path": "/", "timeout": "-1ns", "inherit": false },
  { "path": "/example", "timeout": "-1ns", "inherit": false },
  { "path": "/example/home", "timeout": "1h", "inherit": false },
  { "path": "/example/home/shared", "timeout": "1h", "inherit": true }
]
```

Substitute the IRODS zone for wherever `example` is referenced. The JSON string should be unformatted.

## Examples

Here are some examples to help get started.

### Prepare to Create the Cluster

```
$ ansible-playbook -i /path/to/inventory -K install_k3s.yml
```
