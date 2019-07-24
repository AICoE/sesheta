#!/usr/bin/env python3
# Sesheta
# Copyright(C) 2018,2019
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

"""This is Sesheta -approver bot, she is a Cyborg Team Member of https://github.com/Thoth-Station/."""

import os
import logging

import daiquiri
import sesheta

from github import Github
from github import UnknownObjectException

from sesheta.common import CICD_CONTEXT_ID, get_labels, commit_was_successful_tested, init_github_interface


DEBUG = bool(os.getenv("DEBUG", False))
SESHETA_GITHUB_ACCESS_TOKEN = os.getenv("SESHETA_GITHUB_ACCESS_TOKEN", None)

daiquiri.setup(level=logging.INFO)
logger = daiquiri.getLogger("approver")

if DEBUG:
    logger.setLevel(level=logging.DEBUG)
else:
    logger.setLevel(level=logging.INFO)

logger.info(f"Version v{sesheta.__version__}")


if __name__ == "__main__":
    if not SESHETA_GITHUB_ACCESS_TOKEN:
        logger.error("Github Token not provided via environment variable SESHETA_GITHUB_ACCESS_TOKEN")
        exit(-1)

    github, org, GITHUB_ORGANIZATION, GITHUB_REPOSITORIES, DEFAULT_LABELS = init_github_interface(
        SESHETA_GITHUB_ACCESS_TOKEN, "etc/config.json"
    )

    logger.info(f"Hi, I'm {github.get_user().name}, and I'm fully operational now!")
    logger.debug("... and I am running in DEBUG mode!")

    for _repo in GITHUB_REPOSITORIES:
        logger.info(f"checking Repository '{org.login}/{_repo}' for Pull Requests that could be 'approved'")

        repo = org.get_repo(_repo)

        for pr in repo.get_pulls(state="open"):
            logger.debug(pr)

            labels = get_labels(pr)

            if (
                pr.title.startswith("WIP")
                or pr.title.startswith("[WIP]")
                or ("work-in-progress" in labels)
                or ("do-not-merge/work-in-progress" in labels)
            ):
                logger.info(f"'{pr.title}' is not mergeable, it's work-in-progress!")

                if "work-in-progress" not in labels:
                    pr.as_issue().add_to_labels("work-in-progress")

                continue

            if not pr.mergeable:
                logger.info(f"'{pr.title}' is not mergeable, it needs rebase!")

                pr.as_issue().add_to_labels("needs-rebase")
                continue

            if pr.mergeable and ("needs-rebase" in labels):
                logger.info(f"'{pr.title}' is mergeable, removing 'needs-rebase' label")

                pr.as_issue().remove_from_labels("needs-rebase")

            # if all commits of this PR are CI'd positive, we might approve the PR
            commits = pr.get_commits()
            maybe_approve = False

            for commit in commits:
                statuses = commit.get_statuses()

                if commit_was_successful_tested(commit, statuses):
                    logger.debug(f"commit '{commit}' was successfully tested by {CICD_CONTEXT_ID}")

                    maybe_approve = True

            if maybe_approve:
                logger.info(f"I am going to approve Pull Request '{pr.title}'")
                pr.as_issue().add_to_labels("approved")

            else:
                logger.info(f"Pull Request '{pr.title}' could not be approved due to failed CI")
