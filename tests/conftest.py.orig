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

import json

import pytest


@pytest.fixture()
def pull_request_review_submitted():
    with open('./fixtures/pull_request_review_submitted.json') as f:
        data = json.load(f)

    return data


@pytest.fixture()
def pull_request_review_requested():
    with open('./fixtures/pull_request_review_requested.json') as f:
        data = json.load(f)

    return data
