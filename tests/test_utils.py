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


from sesheta.webhooks import eligible_release_pullrequest, get_release_issue
from sesheta.utils import mattermost_username_by_github_user


class TestPullRequestUtilities(object):  # Ignore PyDocStyleBear
    # Ignore PyDocStyleBear
    def test_eligible_release_pullrequest(self, pull_request_review_requested, pull_request_merged):
        assert pull_request_merged
        assert pull_request_review_requested

        assert eligible_release_pullrequest(pull_request_merged) == True
        assert eligible_release_pullrequest(
            pull_request_review_requested) == False

    # Ignore PyDocStyleBear
    def test_get_release_issue(self, pull_request_review_requested, pull_request_merged):
        assert pull_request_merged
        assert pull_request_review_requested

        assert get_release_issue(pull_request_review_requested) == None
        assert get_release_issue(pull_request_merged) == 15

    def test_mattermost_username_by_github_user(self):
        assert mattermost_username_by_github_user('goern') == '@goern'
        assert mattermost_username_by_github_user('fridex') == '@fridolin'
        assert mattermost_username_by_github_user(
            'ghostbuster') == 'ghostbuster'
