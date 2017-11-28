#!/usr/bin/env python
# -*- coding: utf-8 -*-
#   manageiq-bot
#   Copyright(C) 2017 Christoph Görn
#
#   This program is free software: you can redistribute it and / or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see < http: // www.gnu.org / licenses / >.

"""This is Thoth, a dependency updating bot for the ManageIQ community.
"""

from github import Github

from github_helper import pr_in_progress

from configuration import GITHUB_ACCESS_TOKEN, TRAVIS_REPO_SLUG


def test_pr_in_progress():
    """This test requires internet access"""

    g = Github(login_or_token=GITHUB_ACCESS_TOKEN)

    assert pr_in_progress(g, TRAVIS_REPO_SLUG,
                          'bots-life/updating-hamlit') is True
    assert pr_in_progress(g, TRAVIS_REPO_SLUG, 'pr_does_not_exists') is False
