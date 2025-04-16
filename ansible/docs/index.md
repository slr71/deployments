# DE Deployments

Table of Contents:
- [Required Git Repositories](#required-git-repositories)
- [Continuous Integration To QA](#continuous-integration-to-qa)
- [Production Deployment Automation](#production-deployment-automation)

## Required Git Repositories

There are two publicly available git repositories that are needed for deployments along with a single private repository:

* github.com/cyverse-de/deployments - Contains Ansible playbooks and roles.
* github.com/cyverse-de/de-releases - Contains build JSON files, K8s resource files, and configuration templates.
* A private/interal repository that defines the Ansible inventory and group_vars for a deployment.

For the most part you will be directly interacting with the `deployments` and internal repository. The `de-releases` repository is checked out by playbooks as needed, so you'll only need to grab it if you need to update/add/remove a configuration template or check on a build.json file.

## Continuous Integration To QA

This section describes how builds are automated and deployed to QA. You will want to have access to the following git repositories:

* [cyverse-de/de-releases](https://github.com/cyverse-de/de-releases)
* [cyverse-de/github-workflows](https://github.com/cyverse-de/github-workflows)
* [cyverse-de/deployments](https://github.com/cyverse-de/deployments)

Additionally, you will want access to our CI/CD systems at [cicd-qa.cyverse.org](https://cicd-qa.cyverse.org).

### Builds

At a high-level, our build process is as follows:
 - Commit and make changes in a branch.
 - Submit and merge PR with the changes.
 - Tag revisions with a new version in the format `v#.#.#` such as `v-1.0.1`.
 - Push tags.
 - `skaffold-build.yml` workflow is triggered, which builds the images on Github's systems.
 - The workflow generates a new build JSON file, which gets committed and pushed to the `builds` directory of the `de-releases` repository.
 - The workflow then emits a webhook to our CI/CD system at https://cicd-qa.cyverse.org.

Each repository that contains a deployable should have a `.github/workflows/skaffold-build.yml` file that looks like the following:

```yaml
name: skaffold-build

on:
  push:
    tags:
      - "v[0-9]+.[0-9]+.[0-9]+"
      - "v[0-9]+.[0-9]+.[0-9]+-rc[0-9]+"

jobs:
  call-workflow-passing-data:
    uses: cyverse-de/github-workflows/.github/workflows/skaffold-build.yml@v0.0.7
    with:
      build-prerelease: ${{ contains(github.ref_name, '-rc') }}
    secrets:
      harbor-username: ${{ secrets.HARBOR_USERNAME }}
      harbor-password: ${{ secrets.HARBOR_PASSWORD }}
      releases-repo-push-token: ${{ secrets.GH_DE_RELEASES_PUSH_TOKEN }}
```

As you can see from the `jobs.call-workflow-passing-data.uses` field, this workflow calls out to the `skaffold-build.yml` workflow contained in the [cyverse-de/github-workflows](https://github.com/cyverse-de/github-workflows) repository tagged with `v0.0.7`.

As part of the shared `skaffold-build.yml` file contained in the `cyverse-de/github-workflows` repository, a new JSON artifact file is created in the `builds/` directory of the [cyverse-de/de-releases](https://github.com/cyverse-de/de-releases) repository. An action after that sends a webhook request to [https://cicd-qa.cyverse.org](https://cicd-qa.cyverse.org) to trigger the deployment into the QA cluster. More info on the webhook configuration is provided below.

Deployment
 - GoCD
 - Hosts & roles
 - Pipelines
 - Triggers
 - Usage of templating

## Production Deployment Automation

You'll need the following repositories checked out locally:
 - `deployments`. See [https://github.com/cyverse-de/deployments](https://github.com/cyverse-de/deployments)
 - `de-releases`. See [https://github.com/cyverse-de/de-releases](https://github.com/cyverse-de/de-releases)
 - The private inventory repo.

You'll need the following tools installed:
 - `ansible` at a reasonably recent version. See [https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)
 - `kubectl` at version `1.29` or higher. See [https://kubernetes.io/docs/tasks/tools/](https://kubernetes.io/docs/tasks/tools/)
 - `helm` at version `3.16` or higher. See [https://helm.sh/docs/intro/install/](https://helm.sh/docs/intro/install/)
 - `golang-migrate` at version `4.18` or higher. See [https://github.com/golang-migrate/migrate](https://github.com/golang-migrate/migrate).
 - `postgresql` client tools, namely `psql` at version `14` or higher. See [https://www.postgresql.org/download/](https://www.postgresql.org/download/).
 - `k0sctl` at the latest stable version. See [https://github.com/k0sproject/k0sctl](https://github.com/k0sproject/k0sctl).


First, make sure you have the production kubeconfig. To get it, go into the `prod-deployment` repository's top-level directory and make sure the `main` branch is up to date.

### Get the kubconfig file
Then set the `K0S_SSH_USER` and `K0S_SSH_KEY_PATH` environment variables to the values appropriate for your local environment. For example:

```bash
export K0S_SSH_USER=replace_me
export K0S_SSH_KEY_PATH=~/.ssh/id_rsa.pub
```

Or in `fish`
```bash
set -gx K0S_SSH_USER replace_me
set -gx K0S_SSH_KEY_PATH ~/.ssh/id_rsa.pub
```

Next, you should make sure that your user has passwordless ssh and sudo into the cluster. The SSH part is covered elsewhere, but the passwordless sudo should be doable with the following command:

```bash
ansible k8s_nodes -i $PROD_INVENTORY -K --become -m shell -a "usermod -aG k0s $K0S_SSH_USER"
```

Finally, run the following to generate the kubeconfig. Replace the path with the one you want/need, if needed:
```bash
mkdir -p ~/.kube/
k0sctl kubeconfig > ~/.kube/prod.conf
```

### Set the KUBECONFIG environment variable
You'll also need a kubeconfig file for the production cluster. Set the `KUBECONFIG` environment variable to the path of the kubeconfig file.

For bash:
```bash
export KUBECONFIG=~/.kube/prod.conf
```

For fish:
```bash
set -gx KUBECONFIG ~/.kube/prod.conf
```

### Database migrations
You need to have the `migrate` command available in your PATH. You can get it from [https://github.com/golang-migrate/migrate](https://github.com/golang-migrate/migrate). Download the latest released version appropriate for your operating system and architecture and ensure that the `migrate` binary is in your PATH.

### Setting the path to the de-releases repository
By default, our inventory group vars will override the `de_releases_dir` var to `../../de-releases`. This value places the cloned repository alongside the `deployments` repository when running the ansible commands from the `deployments/ansible` directory.

### Deployment process
Here is the process to deploy a release into an environment. Each line is a separate command:
```bash
ansibly-playbook -i <path/to/private-inventory/inventory/> --tags=setup-databases kubernetes.yml
ansible-playbook -i <path/to/private-inventory/inventory/> --tags=configure-services kubernetes.yml
ansible-playbook -i <path/to/private-inventory/inventory/> --tags=deploy-all-services kubernetes.yml
```

You can run the kubernetes.yml playbook without the tags and it will still run through the steps in order, but it will also attempt to run a bunch more steps that can consume a lot of time and resources. It's recommended to use the tags to limit the tasks that actually run.
