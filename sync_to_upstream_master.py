#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This is thoth, a dependency updating bot...
"""

__version__ = '0.1.0'

import os
import json
import logging
import shutil
import fileinput

from tornado import httpclient
from gemfileparser import GemfileParser

from git import Repo, Actor, RemoteProgress
from git.exc import GitCommandError
from github import Github

from configuration import *

# read in ENV from .env
try:
    from dotenv import load_dotenv, find_dotenv

    load_dotenv(find_dotenv())
except:
    pass

# set up logging
DEBUG_LOG_LEVEL = bool(os.getenv('DEBUG', False))

if DEBUG_LOG_LEVEL:
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s,%(levelname)s,%(filename)s:%(lineno)d,%(message)s')
else:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


def cleanup(directory):
    """clean up the mess we made..."""
    logging.info("Cleaning up workdir: %s" % directory)

    try:
        shutil.rmtree(directory)
    except FileNotFoundError as fnfe:
        logging.info("Non Fatal Error: " + str(fnfe))


if __name__ == '__main__':
    # clone our github repository
    cleanup(LOCAL_WORK_COPY)

    logging.info("Cloning from %s" % MASTER_REPO_URL)
    try:
        logging.info("Cloning git repository %s to %s" %
                     (MASTER_REPO_URL, LOCAL_WORK_COPY))
        repository = Repo.clone_from(MASTER_REPO_URL, LOCAL_WORK_COPY)
    except GitCommandError as git_error:
        logging.error(git_error)
        exit(-1)

    # 1. add upstream as a remote
    repository.create_remote('upstream', UPSTREAM_MASTER_REPO_URL)

    # 2. fetch upstream master and rebase onto it
    logging.info("Fetching from %s" % UPSTREAM_MASTER_REPO_URL)
    repository.remotes.upstream.fetch('master')
    repository.git.rebase('upstream/master')

    # 3. push to remote origin master
    logging.info("Pushing to %s" % MASTER_REPO_URL)
    # FIXME this aint pushing...
    with repository.git.custom_environment(GIT_SSH_COMMAND=SSH_CMD):
        repository.remotes.origin.push('master:master')

    logging.info("Done syncing %s to %s" % (MASTER_REPO_URL, UPSTREAM_MASTER_REPO_URL))
