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

### Pull/Merge Requests requiring rebase

If a 'needs-rebase' label is set on a Pull/Merge Request, a notification will be send out to the DevOps Channel.

## Deploying

To deploy sesheta on an OpenShift cluster use the following Ansible command with required parameters:

```shell
  ansible-playbook \
    --extra-vars=OCP_URL=<openshift_cluster_url> \
    --extra-vars=OCP_TOKEN=<openshift_cluster_token> \
    --extra-vars=SESHETA_CONFIG_FILE=<config_json> \
    --extra-vars=SESHETA_SCRUM_SPACE=<google-chat-space> \
    --extra-vars=SESHETA_SCRUM_URL=<scurm_meeting_url> \
    --extra-vars=SESHETA_APPLICATION_NAMESPACE=<openshift_cluster_namespace> \
    --extra-vars=SESHETA_GITHUB_OAUTH_TOKEN=<github_oauth_token> \
    --extra-vars=SESHETA_SSH_PRIVATE_KEY_PATH=<github_ssh_private_key_path> \
    --extra-vars=SESHETA_GITHUB_WEBHOOK_SECRET=<github_webhook_secret> \
    --extra-vars=SESHETA_GOOGLE_CHAT_ENDPOINT_URL=<google_chat_incoming_webhook_url> \
    playbooks/provision.yaml
```


- `OCP_URL`: The OpenShift cluster host url for establishing connection.

- `OCP_TOKEN`: The OpenShift user token for login into the cluster.

- `SESHETA_CONFIG_FILE`: **SESHETA_CONFIG_FILE** contain configuration json to be provided to sesheta.(Example: '$HOME/AICoE/sesheta/config.json'). configuration file for thoth-station and aicoe is present in the repo and it contains list of repos are to be watched by sesheta. Refer [AICoE Config](config-aicoe.json) and [thoth-station config](config.json)

- `SESHETA_SCRUM_SPACE`: Google Chat Room Space, please refer google chat api documentation to get your room space (Example: spaces/abcd)

- `SESHETA_SCRUM_URL`: URL for the space where scrum call would be held. (Example: bluejeans room url)

- `SESHETA_APPLICATION_NAMESPACE`: The OpenShift namespace can be used for the application purposes, all the templates, builds, secrets, configmap and jobs are stored in the `SESHETA_APPLICATION_NAMESPACE`.

- `SESHETA_GITHUB_OAUTH_TOKEN`: To raise a pull request bot requires user rights and premissions. The GitHub OAuth tokens are to be set for raising pull request whenever updates are encounter by the Sesheta.

- `SESHETA_SSH_PRIVATE_KEY_PATH`: The path where the GitHub ssh private key is stored should be provided. (Example: $HOME/.ssh/id_rsa). If the field is undefined then the script will create the ssh keys for you and then you can set up the given public key to GitHub repository.

- `SESHETA_GITHUB_WEBHOOK_SECRET`: Secret used to secure each webhook send by GitHub.

- `SESHETA_GOOGLE_CHAT_ENDPOINT_URL`: The incoming webhook URL of Google Chat.To Enable Sesheta to send scrum call reminder.

## Copyright

Copyright (C) 2017,2018,2019 Red Hat Inc.

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
