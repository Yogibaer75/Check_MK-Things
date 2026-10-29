#!/usr/bin/python

# License: GNU General Public License v2

import doctest

from cmk.plugins.hyperv_cluster import lib


def test_doctests() -> None:
    assert doctest.testmod(lib).failed == 0
