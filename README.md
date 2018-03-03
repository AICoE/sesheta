# Sesheta

Sesheta is a junior community team member.

[![Dependency Status](https://gemnasium.com/badges/github.com/goern/sesheta.svg)](https://gemnasium.com/github.com/goern/sesheta)

# Deployment

The following sections describe what needs to be done to deploy Sesheta.

## Secrets

Secrets are used for varius API access, either via REST or SSH. Secrets are references by Deployments or CronJobs.

```bash
oc create secret generic sesheta \
 --from-literal=GEMNASIUM_API_KEY=<token> \
 --from-literal=GITHUB_ACCESS_TOKEN=<token> \
 --from-literal=THOTH_DEPENDENCY_BOT_TRAVISCI=<token>
oc secrets new-sshauth github --ssh-privatekey=<ssh_private_key_filename>
```

## BuildConfigurations and ImageStreams

These two build configurations use the git repositories as input, during development it is advices to create corresponding binary builds.

```bash
oc new-build --name patch-bot --to patch-bot --image-stream openshift/python:3.5 https://github.com/AICoE/sesheta
oc new-build --name dependencies --to dependencies --image-stream openshift/python:3.5 https://github.com/AICoE/sesheta
```

## Deployments

`oc create -f dependencies.json`

## Services and Routes

As we want to provide a webhook endpoint, we need to create a service and expose it via a route.

```bash
oc create service clusterip  dependencies --tcp 8080:8080
oc expose service dependencies
```

## CornJob

# Local Testing

`curl -d @test/fixtures/travis-webhooks-one-event.urlencoded -H "Content-Type: application/x-www-form-urlencoded" -X POST http://localhost:8080/webhooks/travis-ci`

# TODO

Implemente pr_in_progress()

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
