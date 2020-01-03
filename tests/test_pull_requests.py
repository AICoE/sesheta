#!/usr/bin/env python3
# Sesheta
# Copyright(C) 2018, 2019, 2020 Christoph Görn
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


from sesheta.utils import calculate_pullrequest_size


class TestPullRequests(object):  # Ignore PyDocStyleBear
    @staticmethod
    # Ignore PyDocStyleBear
    def test_pull_request_size(pull_request_review_requested):
        assert pull_request_review_requested
        assert pull_request_review_requested["action"] == "review_requested"
        assert "requested_reviewers" in pull_request_review_requested.keys()

        assert calculate_pullrequest_size(pull_request_review_requested["pull_request"]) == "size/XS"

    @staticmethod
    # Ignore PyDocStyleBear
    def test_review_approved(pull_request_review_submitted_approved):
        assert pull_request_review_submitted_approved
        assert pull_request_review_submitted_approved["action"] == "submitted"

        assert pull_request_review_submitted_approved["review"]["state"] == "approved"


#        add_labels(
#            pull_request_review_submitted_approved['pull_request']['_links']['issue'], ['approved'])
