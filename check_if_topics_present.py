#!/usr/bin/env python3
# Sesheta
# Copyright(C) 2019 Christoph Görn
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


"""Make sure that all our repos have the minimum topics."""


import json
import logging
import os

import daiquiri
import requests
from requests.auth import HTTPBasicAuth

import sesheta


DEBUG = bool(os.getenv("DEBUG", False))
GITHUB_ACCESS_TOKEN = os.getenv("SESHETA_GITHUB_SRCOPS_ACCESS_TOKEN", None)

daiquiri.setup(level=logging.INFO)
logger = daiquiri.getLogger("topic_checker")

if DEBUG:
    logger.setLevel(level=logging.DEBUG)
else:
    logger.setLevel(level=logging.INFO)

logger.info(f"Version v{sesheta.__version__}")

# lets see what requests is doing
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

_QUERY = """
query GetRepositoriesAndTopics{
    organization(login:"aicoe") {
    repositories(first: 100) {
        edges {
                node {
                    id
                    name
                    repositoryTopics(first: 100){
                        edges {
                            node {
                                topic {
                                    name
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
"""

_MUTATION_TEMPLATE = """
mutation SetRepositoryTopics {{
  updateTopics(input: {{
                repositoryId: "{repository_id}",
                topicNames: {topic_names},
                clientMutationId: "{id}"}}) {{
        clientMutationId
        invalidTopicNames
    }}
}}
"""


class GraphQLClient:
    """GraphQL client."""

    def __init__(self, token):
        """Init with some sane defaults."""
        self.session = requests.Session()
        self.token = token
        self.session.headers.update({"Authorization": f"bearer {token}"})
        self.session.headers.update({"User-Agent": f"thoth_sesheta_topic_checker/{sesheta.__version__}"})

    def request(self, query):
        """Do a GraphQL request."""
        if not self.token:
            raise RuntimeError("Please set an environment variable SESHETA_GITHUB_SRCOPS_ACCESS_TOKEN.\n")

        logger.debug(f"session = {self.session.headers}")
        logger.debug(f"query = {query}")
        response = self.session.post(
            url="https://api.github.com/graphql", json={"query": query}, auth=HTTPBasicAuth("sesheta", self.token)
        )

        return response


if __name__ == "__main__":
    logger.info(f"Hi, I'm sesheta, and I'm fully operational now!")
    logger.debug("... and I am running in DEBUG mode!")

    if not GITHUB_ACCESS_TOKEN:
        logger.error("GitHub Token not provided via environment variable SESHETA_GITHUB_SRCOPS_ACCESS_TOKEN")
        exit(-1)

    G = GraphQLClient(GITHUB_ACCESS_TOKEN)

    repos = G.request(_QUERY).json()["data"]
    logger.debug(repos)

    if "errors" in repos:
        raise RuntimeError("There was something wront with the repos query")

    for repo in repos["organization"]["repositories"]["edges"]:
        repo_id = repo["node"]["id"]
        repo_name = repo["node"]["name"]
        repo_topics = set()

        for topic in repo["node"]["repositoryTopics"]["edges"]:
            if topic["node"]["topic"]["name"] == "ansible-role":
                continue

            repo_topics.add(topic["node"]["topic"]["name"])

        repo_topics.add("artificial-intelligence")
        # repo_topics.add("thoth")

        if "sesheta" in repo_name:
            repo_topics.add("thoth")
            repo_topics.add("sesheta")
            repo_topics.add("bot")
            repo_topics.add("cyborg")

        if ("prometheus" in repo_name) or ("thanos" in repo_name):
            repo_topics.add("prometheus")

        if ("tensorflow" in repo_name) or ("tf-" in repo_name):
            repo_topics.add("tensorflow")

        if repo_name.startswith("zuul"):
            repo_topics.add("zuul")
            repo_topics.add("zuul-ci")

        if repo_name.startswith("ansible-role"):
            repo_topics.add("ansible")
            repo_topics.add("ansible-roles")

        if repo_name.startswith("srcops"):
            repo_topics.add("srcops")

        logger.info(f"repo({repo_id}): {repo_name}: {repo_topics}")

        mutation = G.request(
            _MUTATION_TEMPLATE.format(repository_id=repo_id, topic_names=json.dumps(list(repo_topics)), id="1")
        )

        logger.debug(mutation.json())
