#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This is thoth, a dependency updating bot...
"""

import os
import logging

from pathlib import Path

__version__ = '0.1.0'

try:
    from dotenv import load_dotenv, find_dotenv

    load_dotenv(find_dotenv())
except Exception as e:
    logging.info(e)

# This is for github.com
GITHUB_ORG_NAME = 'goern'
GITHUB_UPSTREAM_ORG_NAME = 'manageiq'
GITHUB_REPO_NAME = 'manageiq'
GITHUB_ACCESS_TOKEN = os.getenv('GITHUB_ACCESS_TOKEN')
MASTER_REPO_URL = 'git@github.com:' + \
    GITHUB_ORG_NAME + '/' + GITHUB_REPO_NAME + '.git'
MASTER_REPO_URL_RO = 'https://github.com/' + \
    GITHUB_ORG_NAME + '/' + GITHUB_REPO_NAME + '.git'
UPSTREAM_MASTER_REPO_URL = 'git@github.com:' + \
    GITHUB_UPSTREAM_ORG_NAME + '/' + GITHUB_REPO_NAME + '.git'

# Travis-CI
TRAVIS_REPO_SLUG = GITHUB_ORG_NAME + '/' + GITHUB_REPO_NAME
THOTH_DEPENDENCY_BOT_TRAVISCI = os.environ.get('THOTH_DEPENDENCY_BOT_TRAVISCI')

# Gemnasium
GEMNASIUM_STATUS_URL = 'https://api.gemnasium.com/v1/projects/goern/manageiq/dependencies'

# DataHub configuration
DATAHUB_REDHAT_INTERNAL = True
DATAHUB_ES_HOSTNAME = 'es-test-elasticsearch.ose.sbu.lab.eng.bos.redhat.com'
DATAHUB_ENDPOINT = 'https://'+DATAHUB_ES_HOSTNAME+'/'
DATAHUB_TRAVISCI_INDEX = 'travisci'
DATAHUB_CERT_PATH = str(Path.cwd()) + '/certs/'
DATAHUB_W_CERT = DATAHUB_CERT_PATH + 'system.logging.fluentd.crt'
DATAHUB_W_KEY = DATAHUB_CERT_PATH + 'system.logging.fluentd.key'
DATAHUB_R_CERT = DATAHUB_CERT_PATH + 'system.logging.kibana.crt'
DATAHUB_R_KEY = DATAHUB_CERT_PATH + 'system.logging.kibana.key'

# local configuration
LOCAL_WORK_COPY = './manageiq-workdir'

# if we are not running on OpenShift...
SSH_CMD = str(Path.cwd()) + '/ssh_command'
os.environ["SSH_CMD"] = SSH_CMD

# whoami
BOT_USERS = ['sesheta']
BOT_EMAILS = ['goern+sesheta@redhat.com']
