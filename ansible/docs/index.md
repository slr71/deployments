# Purpose

## Required Git Repositories

There are two publicly available git repositories that are needed for deployments along with a single private repository:

* github.com/cyverse-de/deployments - Contains Ansible playbooks and roles.
* github.com/cyverse-de/de-releases - Contains build JSON files, K8s resource files, and configuration templates.
* A private/interal repository that defines the Ansible inventory and group_vars for a deployment.

For the most part you will be directly interacting with the `deployments` and internal repository. The `de-releases` repository is checked out by playbooks as needed, so you'll only need to grab it if you need to update/add/remove a configuration template or check on a build.json file.

## Continuous Integration To QA

At a high-level, our build process is as follows:
 - Commit and make changes in a branch.
 - Submit and merge PR with the changes.
 - Tag revisions with a new version in the format `v#.#.#` such as `v-1.0.1`.
 - Push tags.
 - `skaffold-build.yml` workflow is triggered, which builds the images on Github's systems.
 - The workflow generates a new build JSON file, which gets committed and pushed to the `builds` directory of the `de-releases` repository.
 - The workflow then emits a webhook to our CI/CD system at https://cicd-qa.cyverse.org.

Deployment
 - GoCD
 - Hosts & roles
 - Pipelines
 - Triggers
 - Usage of templating

## Production Deployment Automation
