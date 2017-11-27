#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

import github
from github_helper import successful_travis_build_id


@pytest.fixture
def requester():
    return github.Commit.Requester(login_or_token="X")


@pytest.fixture
def headers():
    return github.Commit.Headers()


@pytest.fixture
def attributes():
    return github.Commit.Attributes()


@pytest.fixture
def headers():
    return github.Commit.Headers()


@pytest.fixture
def commit():
    return None # github.Commit.Commit(requester, headers, attributes, True)


def test_successful_travis_build_id(commit):
    # build_id = successful_travis_build_id(commit)
    # assert build_id, 306279075
    # TODO
    pass
