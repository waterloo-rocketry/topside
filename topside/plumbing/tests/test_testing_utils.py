import pytest

import topside as top
import topside.plumbing.invalid_reasons as invalid
import topside.plumbing.exceptions as exceptions
import topside.plumbing.tests.testing_utils as test
import topside.plumbing.plumbing_utils as utils

def test_step():
    conn = {
        (1, 0): [(2, 100, utils.FC_MAX)],
        (2, 100): [1, 0, utils.FC_MAX],
    }
    ret = test.step(conn, utils.DEFAULT_TIME_RESOLUTION_MICROS)

    assert ret == {
        1: 100 * utils.FC_MAX * utils.DEFAULT_RESOLUTION_SCALE,
        2: 100 - 100 * utils.FC_MAX * utils.DEFAULT_RESOLUTION_SCALE
    }

test_step()
