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


"""This is Sesheta, she is a Cyborg Team Member of https://github.com/Thoth-Station/."""


import logging

import yaml
import daiquiri

from github import Github
from github import UnknownObjectException


daiquiri.setup(level=logging.DEBUG, outputs=('stdout', 'stderr'))
_LOGGER = daiquiri.getLogger(__name__)


CICD_CONTEXT_ID = 'continuous-integration/jenkins/pr-merge'
DO_NOT_MERGE_LABELS = ['do-not-merge',
                       'work-in-progress',
                       'do-not-merge/work-in-progress'
                       'do-not-merge/hold'
                       ]


def init_github_interface(SESHETA_GITHUB_ACCESS_TOKEN):  # pragma: no cover
    """init_github_interface will read the configuration and return initilalized github and org objects."""
    github = Github(SESHETA_GITHUB_ACCESS_TOKEN)

    with open("config.yaml", 'r') as config:
        RUNTIME_CONFIG = yaml.load(config)

    GITHUB_ORGANIZATION = RUNTIME_CONFIG['organization']
    GITHUB_REPOSITORIES = RUNTIME_CONFIG['repositories']
    DEFAULT_LABELS = RUNTIME_CONFIG['defaultLabels']

    org = github.get_organization(GITHUB_ORGANIZATION)

    if org is None:
        _LOGGER.error('Can not get a Github Organization or User...')
        exit(-2)

    return github, org, GITHUB_ORGANIZATION, GITHUB_REPOSITORIES, DEFAULT_LABELS


def ensure_label_present(repo, name, color, current_labels, description=''):  # pragma: no cover
    """Ensure the given repo has the label with the right color."""
    present_labels = []

    for label in current_labels:
        present_labels.append(label.name)

    if name not in present_labels:
        _LOGGER.info(f"adding '{name}' label to {repo.name}")

        try:
            repo.create_label(name, color, description)

        except UnknownObjectException as e:
            _LOGGER.error(e)

            repo.create_issue(f"can't create '{name}' label")
            _LOGGER.info('issue created!')
    else:
        _LOGGER.debug(f"label '{name}' was present")


def get_labels(pr) -> list:  # pragma: no cover
    """Extract a list of strings from github.PaginatedList.PaginatedList of github.Label.Label."""
    labels = []

    try:
        _labels = pr.as_issue().get_labels()
        for _label in _labels:
            labels.append(_label.name)
    except AttributeError as e:
        _LOGGER.error(e)

    return labels
