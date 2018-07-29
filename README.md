# Sesheta

Sesheta is a junior community team member. We will reincarnate it over the next weeks...

# Source Operations

## Labels

The following sections describe what Sesheta does with regards to source operations.

### Pull/Merge Request Size Labels

Each Pull/Merge Request will be assigned a size label. Labels are applied based on
the total number of lines of changes (additions and deletions):

- size/XS: 0-9
- size/S: 10-29
- size/M: 30-99
- size/L 100-499
- size/XL: 500-999
- size/XXL: 1000+

## Deploying

To deploy sesheta on an OpenShift cluster use the following Ansible command with required parameters:

```shell
  ansible-playbook \
    --extra-vars=SESHETA_INFRA_NAMESPACE=<openshift_cluster_namespace> \
    --extra-vars=SESHETA_APPLICATION_NAMESPACE=<openshift_cluster_namespace> \
    --extra-vars=SESHETA_TOKEN=<github_oauth_token> \
    --extra-vars=SESHETA_SSH_PRIVATE_KEY_PATH=<github_ssh_private_key_path> \
    --extra-vars=SESHETA_GITHUB_WEBHOOK_SECRET=<github_webhook_secret> \
    --extra-vars=SESHETA_MATTERMOST_ENDPOINT_URL=<mattermost_incoming_webhook_url> \
    playbooks/provision.yaml
```

- `KEBECHET_SSH_PRIVATE_KEY_PATH`: The path where the GitHub ssh private key is stored should be provided. (Example: $HOME/.ssh/id_rsa). If the field is undefined then the script will create the ssh keys for you and then you can set up the given public key to GitHub repository.

- `KEBECHET_TOKEN`: To raise a pull request bot requires user rights and premissions. The GitHub OAuth tokens are to be set for raising pull request whenever updates are encounter by the Kebechet.

- `KEBECHET_CONFIGURATION_PATH`: Path to the YAML configuration file to be used for Kebechet to check for dependency updates.

- `KEBECHET_INFRA_NAMESPACE`: The OpenShift namespace can be used for the infrastructural purposes, all the images stream are stored in the `KEBECHET_INFRA_NAMESPACE`.

- `KEBECHET_APPLICATION_NAMESPACE`: The OpenShift namespace can be used for the application purposes, all the templates, builds, secrets, configmap and jobs are stored in the `KEBECHET_APPLICATION_NAMESPACE`.

- `SESHETA_GITHUB_WEBHOOK_SECRET`: Secret used to secure each webhook send by GitHub.

- `SESHETA_MATTERMOST_ENDPOINT_URL`: The incoming webhook URL of Mattermost.

## Copyright

Copyright (C) 2017,2018 Red Hat Inc.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

The GNU General Public License is provided within the file LICENSE.
