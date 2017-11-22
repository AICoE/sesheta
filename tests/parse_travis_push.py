#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This is thoth, a dependency updating bot...
"""

__version__ = '0.1.0'

import os
import json
import logging
import shutil

from github import Github

MASTER_REPO_URL = 'git@github.com:goern/manageiq.git'
GITHUB_REPO_NAME = 'manageiq'
TRAVIS_REPO_SLUG = 'goern/'+GITHUB_REPO_NAME

try:
    from dotenv import load_dotenv, find_dotenv

    load_dotenv(find_dotenv())
except Exception as e:
    logging.warning(e)

DEBUG_LOG_LEVEL = bool(os.getenv('DEBUG', False))

if DEBUG_LOG_LEVEL:
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s,%(levelname)s,%(filename)s:%(lineno)d,%(message)s')
else:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


def create_pr_to_master(target_branch):
    """create a github pr from target_branch to master"""
    git = Github(os.environ.get('GITHUB_ACCESS_TOKEN'))
    repo = git.get_user().get_repo('manageiq')

    repo.create_pull('[Thoth] automated minor update of one dependency',
                     'This PR is generated as part of an automated update, created by Thoth Dependency Bot', 'master', target_branch)



travis_input = json.load(open('fixtures/travis-passed.json'))

for hook in travis_input:
    if ('success' in hook['state'] and
            hook['branches'][0]['name'] != 'master'):
        print(json.dumps(hook['branches'][0]['name']))

        create_pr_to_master(hook['branches'][0]['name'])
