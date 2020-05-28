import pytest

import topside as top
import topside.plumbing.invalid_reasons as invalid
import topside.plumbing.exceptions as exceptions
import topside.plumbing.tests.testing_utils as test
import topside.plumbing.plumbing_utils as utils


def test_step():
    conn = {
        (1, 0): [(2, 100, utils.FC_MAX)],
        (2, 100): [(1, 0, utils.FC_MAX)],
    }
    ret = test.step(conn, utils.micros_to_s(utils.DEFAULT_TIME_RESOLUTION_MICROS))

    assert ret == {
        1: 100 * utils.FC_MAX * utils.micros_to_s(utils.DEFAULT_TIME_RESOLUTION_MICROS),
        2: 100 - 100 * utils.FC_MAX * utils.micros_to_s(utils.DEFAULT_TIME_RESOLUTION_MICROS)
    }
    print(utils.FC_MAX)
    print(ret)
