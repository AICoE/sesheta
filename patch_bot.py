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

import semver
from tornado import httpclient
from gemfileparser import GemfileParser

from git import Repo, Actor
from git.exc import GitCommandError
from github import Github

MASTER_REPO_URL = 'git@github.com:goern/manageiq.git'
GEMNASIUM_STATUS_URL = 'https://api.gemnasium.com/v1/projects/goern/manageiq/dependencies'
GITHUB_REPO_NAME = 'manageiq'
LOCAL_WORK_COPY = './manageiq-workdir'
SSH_CMD = 'ssh -i id_deployment_key'

try:
    from dotenv import load_dotenv, find_dotenv

    load_dotenv(find_dotenv())
except:
    pass

DEBUG_LOG_LEVEL = bool(os.getenv('DEBUG', False))

if DEBUG_LOG_LEVEL:
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s,%(levelname)s,%(filename)s:%(lineno)d,%(message)s')
else:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name



def major(semverlike):
    _semver = None
    try:
        _semver = semver.parse(semverlike)['major']
    except ValueError as ve:
        logging.error("%s: %s" %(ve, semverlike))
        _semver = semverlike.split('.')[0]

    return _semver


def minor(semverlike):
    _semver = None
    try:
        _semver = semver.parse(semverlike)['minor']
    except ValueError as ve:
        logging.error("%s: %s" % (ve, semverlike))
        _semver = semverlike.split('.')[1]

    return _semver


def get_dependency_status(slug):
    http_client = httpclient.HTTPClient()

    try:
        req = httpclient.HTTPRequest(url=GEMNASIUM_STATUS_URL,
                                     auth_username='X',
                                     auth_password=os.getenv('GEMNASIUM_API_KEY'))
        response = http_client.fetch(req)

        with open('gemnasium-manageiq.json', 'w') as file:
            file.write(response.body.decode("utf-8"))
    except httpclient.HTTPError as e:
        # HTTPError is raised for non-200 responses; the response
        # can be found in e.response.
        logging.error(e)
    except Exception as e:
        # Other errors are possible, such as IOError.
        logging.error(e)
    http_client.close()

    # TODO handle exceptions
    data = json.load(open('gemnasium-manageiq.json'))

    return data


def bump_minor(package):
    logging.info("updating %s to %s" % (package['name'],
                                        package['distributions']['stable']))

    OWD = os.getcwd()
    os.chdir(LOCAL_WORK_COPY)

    parser = GemfileParser('Gemfile', 'manageiq')
    deps = parser.parse()

    for key in deps:
        if deps[key]:
            for dependency in deps[key]:
                if dependency.name == package['name']:
                    with fileinput.input(files=('Gemfile'), inplace=True, backup='.swp') as f:
                        for line in f:
                            if '"' + dependency.name + '"' in line:
                                line = line.replace(dependency.requirement,
                                                    package['distributions']['stable'], 1)

                            print(line)

    os.chdir(OWD)


def cleanup(directory):
    """clean up the mess we made..."""
    try:
        shutil.rmtree(directory)
    except FileNotFoundError as fnfe:
        logging.info("Non Fatal Error: " + str(fnfe))


def pr_in_progress(target_branch):
    """pr_in_progress() will check if there is an open PR from target_branch to master"""
    # TODO
    return not True


def create_pr_to_master(target_branch):
    """create a github pr from target_branch to master"""
    git = Github(os.environ.get('GITHUB_ACCESS_TOKEN'))
    repo = git.get_user().get_repo(GITHUB_REPO_NAME)

    repo.create_pull('automated update',
                     'This PR is generated as part of an automated update, Sincerely Thoth Dependency Bot', 'master', target_branch)


if __name__ == '__main__':
    # clone our github repository
    cleanup(LOCAL_WORK_COPY)
    try:
        repository = Repo.clone_from(MASTER_REPO_URL, LOCAL_WORK_COPY)
    except GitCommandError as git_error:
        logging.error(git_error)
        exit(-1)

    # and request current status from gemnasium
    deps = get_dependency_status('goern/manageiq')

    # lets have a look at all dependencies
    for dep in deps:
        if dep['color'] == 'yellow': # and at first, just the yellow ones
            # if we have no major version shift, lets update the Gemfile
            if ((major(dep['locked']) == major(dep['package']['distributions']['stable'])) and
                    (minor(dep['locked']) < minor(dep['package']['distributions']['stable']))):
                target_branch = 'bots-life/updating-' + dep['package']['name']

                if not pr_in_progress(target_branch):
                    # 1. create a new branch
                    new_branch = repository.create_head(target_branch)
                    new_branch.checkout()

                    # 2. update Gemfile
                    bump_minor(dep['package'])

                    # 3. commit work
                    repository.index.add(['Gemfile'])
                    author = Actor('Thoth Dependency Bot', 'goern+thoth@redhat.com')
                    committer = Actor('Thoth Dependency Bot',
                                      'goern+thoth@redhat.com')
                    repository.index.commit('Updating {} from {} to {}'.format(dep['package']['name'], dep['locked'], dep['package']['distributions']['stable']),
                                            author=author, committer=committer)

                    # 4. push to origin
                    with repository.git.custom_environment(GIT_SSH_COMMAND=SSH_CMD):
                        repository.remotes.origin.push(refspec='{}:{}'.format(
                            target_branch, target_branch))

                    # 5. and create PR
                    # TODO

                    # 6. checkout master
                    repository.refs.master.checkout()
                else:
                    logging.info("There is an open PR for %s, aborting..." %
                        (target_branch))               

            else:
                logging.info("%s %s(%s) -> %s" % (dep['package']['name'],
                                                 dep['locked'], major(dep['locked']), dep['package']['distributions']['stable']))
