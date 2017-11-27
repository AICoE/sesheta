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
from github_helper import Checklist, successful_travis_build_id

try:
    from dotenv import load_dotenv, find_dotenv

    load_dotenv(find_dotenv())
except Exception as e:
    logging.warning(e)


DEBUG_LOG_LEVEL = bool(os.getenv('DEBUG', False))

GITHUB_ORG_NAME = 'goern'
GITHUB_REPO_NAME = 'manageiq'
GITHUB_ACCESS_TOKEN = os.getenv('GITHUB_ACCESS_TOKEN')
MASTER_REPO_URL = 'git@github.com:' + \
    GITHUB_ORG_NAME + '/' + GITHUB_REPO_NAME + '.git'
TRAVIS_REPO_SLUG = GITHUB_ORG_NAME + '/' + GITHUB_REPO_NAME

BOT_USERS = ['sesheta']

if DEBUG_LOG_LEVEL:
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s,%(levelname)s,%(filename)s:%(lineno)d,%(message)s')
else:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


def create_bot_tasklist(repo_slug):
    global g

    repo = g.get_repo(repo_slug)
    bot_label = repo.get_label('bot')

    tasks_list = Checklist("have a look at this tasks and take care:")
    tasks_list.add("create PR if Travis-CI is green")

    repo.create_issue('please take action', 
                        body=tasks_list.body, labels=[bot_label])
    

def handle_open_tasks(repo_slug):
    repo = g.get_repo(repo_slug)
    bot_label = repo.get_label('bot')
    issues = repo.get_issues(state='open', labels=[bot_label])

    for issue in issues:
        if not issue.pull_request:
            tasks_list = Checklist(issue.body)

            for item, checked in tasks_list.items.items():
                if not checked:
                    tasks_list.check(item)
                    tasks_list.add('@goern please review')

                    issue.edit(body=tasks_list.body)

def check_if_PR_ready_to_merge(repo_slug):
    repo = g.get_repo(repo_slug)
    bot_label = repo.get_label('bot')
    prs = repo.get_pulls(state='open')

    _merge = "   "
    _successful_builds = set()

    for pr in prs:
        if pr.mergeable:
            _merge =" 👍 "

        print(_merge + " " + str(pr.id) + " " + pr.title)

        for commit in pr.get_commits():
           print("\t"+commit.commit.message)
           print("\t\tTravsi-CI Build ID: " + successful_travis_build_id(commit))

def main():
#    create_bot_tasklist(TRAVIS_REPO_SLUG)
#    handle_open_tasks(TRAVIS_REPO_SLUG)
    check_if_PR_ready_to_merge(TRAVIS_REPO_SLUG)

if __name__ == '__main__':
    if not GITHUB_ACCESS_TOKEN:
        logging.error("No GITHUB_ACCESS_TOKEN")
        exit(-1)

    g = Github(login_or_token=GITHUB_ACCESS_TOKEN)
    logging.info("I am " + g.get_user().name)

    main()
