#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib.parse import urlparse
import logging

class Checklist():
    def __init__(self, body=None):
        self.process(body or "")

    @staticmethod
    def format_line(item, check):
        status = ""
#        if isinstance(check, basestring):
#            status = check + ": "
#            check = False
        return " * [{0}] {1}{2}".format(check and "x" or " ", status, item)

    @staticmethod
    def parse_line(line):
        check = item = None
        stripped = line.strip()
        if stripped[:6] in ["* [ ] ", "- [ ] ", "* [x] ", "- [x] ", "* [X] ", "- [X] "]:
            status, unused, item = stripped[6:].strip().partition(": ")
            if not item:
                item = status
                status = None
            if status:
                check = status
            else:
                check = stripped[3] in ["x", "X"]
        return (item, check)

    def process(self, body, items={}):
        self.items = {}
        lines = []
        items = items.copy()
        for line in body.splitlines():
            (item, check) = self.parse_line(line)
            if item:
                if item in items:
                    check = items[item]
                    del items[item]
                    line = self.format_line(item, check)
                self.items[item] = check
            lines.append(line)
        for item, check in items.items():
            lines.append(self.format_line(item, check))
            self.items[item] = check
        self.body = "\n".join(lines)

    def check(self, item, checked=True):
        self.process(self.body, {item: checked})

    def add(self, item):
        self.process(self.body, {item: False})

    def delete(self, item):
        self.process(self.body, {item: None})


def successful_travis_build_id(commit):
    """successful_travis_build_id() will return the Travis-CI Build ID of the last successful build of the given Github commit."""
    _successful_builds = set()

    # FIXME need exception handling
    for status in commit.get_statuses():
        if status.context == 'continuous-integration/travis-ci/push':
            if status.state == 'success':
                _successful_builds.add(travis_build_id(status.target_url))

    return _successful_builds.pop()


def travis_build_id(target_url):
    """travis_build_id() will return the Travis-CI Build ID from a target_url (as found in a github status entity)."""
    # FIXME need exception handling

    return urlparse(target_url).path.split('/')[4]


def pr_in_progress(github, repo_slug, target_branch):
    """pr_in_progress() will check if there is an open PR from target_branch to master"""
    
    _found_it = False

    repo = github.get_repo(repo_slug)
    bot_label = repo.get_label('bot')
    pulls = repo.get_pulls()

    for pr in pulls:
        if pr.state == 'open':
            if target_branch == 'bots-life/updating-' + pr.title.split(': ')[1]:
                _found_it = True

    return _found_it
