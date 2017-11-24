#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This is thoth, a dependency updating bot...
"""

import os
from pathlib import Path

__version__ = '0.1.0'

# This is for github.com
GITHUB_ORG_NAME = 'goern'
GITHUB_UPSTREAM_ORG_NAME = 'manageiq'
GITHUB_REPO_NAME = 'manageiq'
GITHUB_ACCESS_TOKEN = os.getenv('GITHUB_ACCESS_TOKEN')
MASTER_REPO_URL = 'git@github.com:' + \
    GITHUB_ORG_NAME + '/' + GITHUB_REPO_NAME + '.git'
UPSTREAM_MASTER_REPO_URL = 'git@github.com:' + \
    GITHUB_UPSTREAM_ORG_NAME + '/' + GITHUB_REPO_NAME + '.git'

# Travis-CI
TRAVIS_REPO_SLUG = GITHUB_ORG_NAME + '/' + GITHUB_REPO_NAME
THOTH_DEPENDENCY_BOT_TRAVISCI = os.environ.get('THOTH_DEPENDENCY_BOT_TRAVISCI')

# Gemnasium
GEMNASIUM_STATUS_URL = 'https://api.gemnasium.com/v1/projects/goern/manageiq/dependencies'

# local configuration
LOCAL_WORK_COPY = './manageiq-workdir'
SSH_CMD = str(Path.cwd()) + '/ssh_command'
os.environ["SSH_CMD"] = SSH_CMD

# whoami
BOT_USERS = ['sesheta']
