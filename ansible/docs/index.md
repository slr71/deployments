# Purpose

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
