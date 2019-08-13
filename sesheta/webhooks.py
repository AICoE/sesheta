#!/usr/bin/env python3
# Sesheta
# Copyright(C) 2018,2019 Christoph Görn
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


"""This will handle all the GitHub webhooks."""


import os
import logging
import hmac
import json

import daiquiri
import requests

from flask import request, Blueprint, jsonify, current_app
from IGitt.GitHub.GitHubRepository import GitHubRepository
from IGitt.GitHub.GitHubIssue import GitHubToken, GitHubIssue

from sesheta.utils import (
    notify_channel,
    random_positive_emoji,
    random_positive_emoji2,
    calculate_pullrequest_size,
    set_size,
)
from sesheta.webhook_processors.github_reviews import *
from sesheta.webhook_processors.github_pull_requests import *
from sesheta.webhook_processors.github_issue_analyzer import analyse_github_issue


daiquiri.setup(level=logging.DEBUG, outputs=("stdout", "stderr"))
_LOGGER = daiquiri.getLogger(__name__)
_RELATED_REGEXP = r"\w+:\ \#([0-9]+)"
_DRY_RUN = os.environ.get("SESHETA_DRY_RUN", False)
_SESHETA_GITHUB_ACCESS_TOKEN = os.getenv("SESHETA_GITHUB_ACCESS_TOKEN", None)
_SESHETA_GITHUB_WEBHOOK_SECRET = os.getenv("SESHETA_GITHUB_WEBHOOK_SECRET", None)
_GIT_API_REQUEST_HEADERS = {"Authorization": "token %s" % _SESHETA_GITHUB_ACCESS_TOKEN}


webhooks = Blueprint("webhook", __name__, url_prefix="")


def handle_github_open_issue(issue: dict, repository: dict) -> None:  # pragma: no cover
    """Will handle with care."""
    _LOGGER.info(f"An Issue has been opened: {issue['url']}")

    if issue["title"].startswith("Automatic update of dependency"):
        _LOGGER.info(f"{issue['url']} is an 'automatic update of dependencies', not sending notification")
        return

    if issue["title"].startswith("Initial dependency lock"):
        _LOGGER.info(f"{issue['url']} is an 'automatic dependency lock', not sending notification")
        return

    if issue["title"].startswith("Failed to update dependencies to their latest version"):
        _LOGGER.info(f"{issue['url']} is an 'failed to update dependencies', not sending notification")
        return

    notify_channel(
        "new_issue", f"{issue['user']['login']} just opened an issue: {issue['title']}... 🚨", issue["html_url"]
    )

    analysis = analyse_github_issue(issue)

    if "flake" in analysis["status"].keys():
        _LOGGER.debug(f"{issue['number']} seems to be a flake: {analysis['status']['reason']}")

        repo = GitHubRepository(GitHubToken(_SESHETA_GITHUB_ACCESS_TOKEN), repository["full_name"])

        try:
            repo.create_label("flake", "#f3ccff")
            repo.create_label("human_intervention_required", "#f3ccff")
            repo.create_label("potential_flake", "#f3ccff")
        except IGitt.ElementAlreadyExistsError as excptn:
            _LOGGER.error(excptn)

        igitt_issue = GitHubIssue(GitHubToken(_SESHETA_GITHUB_ACCESS_TOKEN), repository["full_name"], issue["number"])
        labels = igitt_issue.labels
        labels.add("human_intervention_required")
        labels.add("potential_flake")
        igitt_issue.labels = labels


def eligible_release_pullrequest(pullrequest: dict) -> bool:
    """Check if the merged Pull Request is eligible to trigger a release."""
    # check if we have the 'bots' label
    try:
        if not any(label.get("name", None) == "bot" for label in pullrequest["labels"]):
            _LOGGER.debug(
                f"No 'bot' label on Release Pull Request: '{pullrequest['title']}', not eligible for release!"
            )
            return False
    except KeyError as exc:
        _LOGGER.debug(f"Not any label on Release Pull Request")
        _LOGGER.exception(exc)
        return False

    # check if Kebechet was the author pullrequest['user']['login']
    if pullrequest["user"]["login"] != "sesheta":
        _LOGGER.debug(
            f"Author of Release Pull Request: '{pullrequest['title']}' is not 'Sesheta', not eligible for release!"
        )
        return False

    return True


def get_release_issue(pullrequest: dict) -> int:
    """Figure out which Issue is related to this Release Pull Request."""
    try:
        # TODO maybe we need to split the body by \n and process each line?!
        for line in pullrequest["body"].splitlines():
            if line.upper().startswith("RELATED"):
                _, issue = line.split("#", maxsplit=1)
                return int(issue)  # FIXME this might fail
    except KeyError as exc:
        return None

    return None


def handle_github_open_pullrequest_merged_successfully(pullrequest: dict) -> None:  # pragma: no cover
    """Will handle with care."""
    _LOGGER.info(f"A Pull Request has been successfully merged: '{pullrequest['title']}'")

    # we simply not notify the DevOps crew about atomated dependency updates
    if pullrequest["title"].startswith("Automatic update of dependency"):
        return

    if pullrequest["title"].startswith("Initial dependency lock"):
        return

    # and we check if we should create a release...
    if pullrequest["title"].startswith("Release of"):
        if not eligible_release_pullrequest(pullrequest):
            _LOGGER.warning(f"Merged Release Pull Request: '{pullrequest['title']}', not eligible for release!")
            return

        commit_hash = pullrequest["merge_commit_sha"]
        release_issue = get_release_issue(pullrequest)
        # TODO this could use a try-except
        release = pullrequest["head"]["ref"][1:]

        # tag
        _LOGGER.info(f"Tagging release {release}: hash {commit_hash}.")

        tag = {"tag": str(release), "message": f"v{release}\n", "object": str(commit_hash), "type": "commit"}

        r = requests.post(
            f"{pullrequest['base']['repo']['url']}/git/tags", headers=_GIT_API_REQUEST_HEADERS, data=json.dumps(tag)
        )

        if r.status_code == 201:
            tag_sha = r.json()["sha"]

            tag_ref = {"ref": f"refs/tags/{release}", "sha": f"{tag_sha}"}

            requests.post(
                f"{pullrequest['base']['repo']['url']}/git/refs",
                headers=_GIT_API_REQUEST_HEADERS,
                data=json.dumps(tag_ref),
            )

        # comment on issue
        _LOGGER.info(f"Commenting on {release_issue} that we tagged {release} on hash {commit_hash}.")

        comment = {
            "body": f"I have tagged commit "
            f"[{commit_hash}](https://github.com/thoth-station/srcops-testing/commit/{commit_hash}) "
            f"as release {release} :+1:"
        }

        requests.post(
            f"{pullrequest['base']['repo']['url']}/issues/{release_issue}/comments",
            headers=_GIT_API_REQUEST_HEADERS,
            data=json.dumps(comment),
        )

        # close issue
        _LOGGER.info(f"Closing {release_issue}.")

        requests.patch(
            f"{pullrequest['base']['repo']['url']}/issues/{release_issue}",
            headers=_GIT_API_REQUEST_HEADERS,
            data=json.dumps({"state": "closed"}),
        )

        if not _DRY_RUN:
            notify_channel(
                "new_tag",
                f" I have tagged {commit_hash} to be release {release} of"
                f" {pullrequest['base']['repo']['full_name']} " + random_positive_emoji2(),
                pullrequest["url"],
            )

        # happy! 💕
    else:
        # otherwise we notify of merge
        if not _DRY_RUN:
            notify_channel(
                "merged_pull_request",
                random_positive_emoji2() + f" Pull Request '{pullrequest['title']}' was successfully "
                f"merged into '{pullrequest['base']['repo']['full_name']}' ",
                pullrequest["url"],
            )

    return


def _add_size_label(pullrequest: dict) -> None:  # pragma: no cover
    """Add a size label to a GitHub Pull Request."""
    if pullrequest["title"].startswith("Automatic update of dependency"):
        return

    if pullrequest["state"] == "closed":
        return

    sizeLabel = calculate_pullrequest_size(pullrequest)

    _LOGGER.debug(f"Calculated the size of {pullrequest['html_url']} to be: {sizeLabel}")

    if sizeLabel:
        # TODO check if there is a size label, if it is the same: skip
        # otherwise update
        set_size(pullrequest["_links"]["issue"]["href"], sizeLabel)


@webhooks.route("/github", methods=["POST"])
def handle_github_webhook():  # pragma: no cover
    """Entry point for github webhook."""
    event = request.headers.get("X-GitHub-Event", "ping")
    if event == "ping":
        return jsonify({"msg": "pong"})

    signature = request.headers.get("X-Hub-Signature")
    sha, signature = signature.split("=")

    secret = str.encode(_SESHETA_GITHUB_WEBHOOK_SECRET)

    hashhex = hmac.new(secret, request.data, digestmod="sha1").hexdigest()

    if hmac.compare_digest(hashhex, signature):
        payload = request.json
        action = ""

        try:
            if "action" in payload.keys():
                action = payload["action"]
        except KeyError as exc:
            _LOGGER.exception(exc)

        _LOGGER.debug(f"Received a webhook: event: {event}, action: {action}.")

        if event == "pull_request":
            _add_size_label(payload["pull_request"])

            if action == "opened":
                process_github_open_pullrequest(payload["pull_request"])
            elif action == "closed":
                if payload["pull_request"]["merged"]:
                    handle_github_open_pullrequest_merged_successfully(payload["pull_request"])
            elif action == "review_requested":
                process_github_pull_request_review_requested(payload["pull_request"])
            elif action == "labeled":
                process_github_pull_request_labeled(payload["pull_request"])
        elif event == "issues":
            if payload["action"] == "opened":
                handle_github_open_issue(payload["issue"], payload["repository"])
        elif event == "pull_request_review":
            process_github_pull_request_review(payload["pull_request"], payload["review"])

    else:
        _LOGGER.error(f"Webhook secret mismatch: me: {hashhex} != them: {signature}")

    return jsonify({"message": "thanks!"}), 200


@webhooks.route("/prometheus", methods=["POST"])
def handle_prometheus_alert_webhook():  # pragma: no cover
    """Entry point for prometheus alert webhook."""
    payload = request.json
    url = payload["externalURL"]
    if payload["status"] == "firing":
        alert_color = "#ff0000"
    else:
        alert_color = "#008000"
    notify_channel(
        "prometheus_alert",
        f"🔎 <font color='{alert_color}'>Prometheus Alert 🚨</font>: \n"
        f"<b>{payload['commonLabels']['alertname']}</b>"
        f" in instance <b>{payload['commonLabels']['instance']}</b>.\n"
        f"Job: <b>{payload['commonLabels']['job']}</b> \n"
        f"Severity: <font color='{alert_color}'>{payload['commonAnnotations']['severity']}</font>\n"
        f"<b>Status</b>: <font color='{alert_color}'>{payload['status']}</font>",
        url,
    )

    return jsonify({"message": "thanks!"}), 200
