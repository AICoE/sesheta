#!/usr/bin/env python3
# Sesheta
# Copyright(C) 2018 Christoph Görn
#
# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


"""test..."""

import os

from IGitt.GitHub.GitHubIssue import GitHubToken, GitHubIssue

from sesheta.webhook_processors.github_issue_analyzer import analyse_github_issue


SESHETA_GITHUB_ACCESS_TOKEN = os.getenv('SESHETA_GITHUB_ACCESS_TOKEN', None)


class TestIssues(object):  # Ignore PyDocStyleBear
    @staticmethod
    # Ignore PyDocStyleBear
    def test_analyse_github_issue(issue115):
        assert issue115['url'] == "https://api.github.com/repos/thoth-station/package-extract/issues/115"

        analysis = analyse_github_issue(issue115)

        assert analysis['status']['flake'] == True
