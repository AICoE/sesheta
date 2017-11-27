#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""I will update a github issue to reflect what I figured out via travis-ci
"""

__version__ = '0.1.0'

import os
import json
import logging
import urllib
import shutil

from travispy import TravisPy
from github import Github
from github_helper import Checklist, successful_travis_build_id
from configuration import *

DEBUG_LOG_LEVEL = bool(os.getenv('DEBUG', False))

if DEBUG_LOG_LEVEL:
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s,%(levelname)s,%(filename)s:%(lineno)d,%(message)s')
else:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


def build_status_image_markdown(github_org_name, github_repo_name, commit_branch):
    return "[![Build Status](https://travis-ci.org/{}/{}.svg?branch={})](https://travis-ci.org/{}/{})".format(github_org_name, github_repo_name, urllib.parse.quote(commit_branch), github_org_name, github_repo_name)

def delete_task(repo_slug, task_issue_id, commit_branch):
    global g

    logging.debug("try to delete %s from tracking issue %s" % (commit_branch, task_issue_id))

    issue = g.get_repo(repo_slug).get_issue(task_issue_id)
    tasks_list = Checklist(issue.body)
    
    for item, checked in tasks_list.items.items():
        if not checked:
            package_name = ''.join(commit_branch.split('-')[2:])

            logging.debug("%s: %s: %s" %
                          (commit_branch, package_name, item))
             
            # FIXME this chk might be a little bit to weak
            if item.startswith(package_name):  
                tasks_list.delete(item)
                tasks_list.add(item.replace(package_name, "~~" + package_name + "~~") +
                               build_status_image_markdown(GITHUB_ORG_NAME, GITHUB_REPO_NAME, commit_branch))
                tasks_list.check(item.replace(package_name, "~~" + package_name + "~~") +
                                 build_status_image_markdown(GITHUB_ORG_NAME, GITHUB_REPO_NAME, commit_branch))
                print(tasks_list.body)
                # issue.edit(body=tasks_list.body)


def get_task_issue_id(repo_slug):
    global g

    issues = g.search_issues(
        '[Thoth] proposing minor updates+in:title+type:issue+labels:bot')

    return issues[0].number


if __name__ == '__main__':
    if not GITHUB_ACCESS_TOKEN:
        logging.error("No GITHUB_ACCESS_TOKEN")
        exit(-1)

    if not GITHUB_ACCESS_TOKEN: # this is used for travis too
        logging.error("No TRAVISCI_ACCESS_TOKEN")
        exit(-1)

    t = TravisPy.github_auth(GITHUB_ACCESS_TOKEN)
    logging.debug("At Travis-CI I am " + t.user().login)

    r = t.repo(TRAVIS_REPO_SLUG)

    g = Github(login_or_token=GITHUB_ACCESS_TOKEN)
    logging.debug("For Github I am " + g.get_user().name)

    TASK_ISSUE_ID = get_task_issue_id(TRAVIS_REPO_SLUG)

    logging.debug("looking at " + TRAVIS_REPO_SLUG)
    for b in t.builds(repository_id=r.id):
        if not b.successful:
            logging.debug("BLD-FL {}: {}".format(b.id, b.commit.branch))
            delete_task(TRAVIS_REPO_SLUG, TASK_ISSUE_ID, b.commit.branch)
        else:
            logging.debug("BLD-OK {}: {}: {}".format(
                b.id, b.commit.branch, b.commit.committer_email))
