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


"""This analyses GitHub Issues."""

import logging

import daiquiri


daiquiri.setup(level=logging.DEBUG, outputs=("stdout", "stderr"))
_LOGGER = daiquiri.getLogger(__name__)


def analyse_github_issue(issue: dict) -> dict:
    """Will analyse a GitHub issue and categorize it."""
    result = {"url": issue["url"], "status": {}}

    for line in issue["body"].splitlines():
        if "Failed to establish a new connection: [Errno -2] Name or service not known" in line:
            result["status"].update(
                {"flake": True, "reason": "Failed to establish a new connection: [Errno -2] Name or service not known"}
            )
        elif "pexpect.exceptions.TIMEOUT: <pexpect.popen_spawn.PopenSpawn" in line:
            result["status"].update(
                {"flake": True, "reason": "pexpect.exceptions.TIMEOUT: <pexpect.popen_spawn.PopenSpawn>"}
            )

    return result
