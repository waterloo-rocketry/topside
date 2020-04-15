import topside as ops
import topside.plumbing.plumbing_utils as utils


def test_teq_to_FC():
    reasonable_max_teq = 1000
    absurdly_large_teq = 100000000

    assert utils.teq_to_FC(0) == utils.FC_MAX
    assert utils.teq_to_FC(utils.CLOSED_KEYWORD) == 0
    for i in range(utils.TEQ_MIN, reasonable_max_teq, 5):
        assert utils.teq_to_FC(i) == 4.5 / i
    assert utils.teq_to_FC(absurdly_large_teq) == 4.5 / absurdly_large_teq


def test_FC_to_teq():
    assert utils.FC_to_teq(0) == utils.CLOSED_KEYWORD

    increment = utils.FC_to_teq(utils.DEFAULT_TIME_RESOLUTION_MICROS)
    i = utils.FC_to_teq(utils.DEFAULT_TIME_RESOLUTION_MICROS)
    while i < utils.FC_MAX:
        assert utils.FC_to_teq(i) == 4.5 / i
        i += increment


def test_micros_to_s():
    large_micros_amount = 100000000

    epsilon = 1e-8
    for i in range(0, large_micros_amount, 100):
        assert abs(utils.micros_to_s(i) - (i / 1e6)) < epsilon


def test_s_to_micros():
    large_second_amount = 1000

    epsilon = 1e-8
    i = 0
    while i < large_second_amount:
        assert abs(utils.s_to_micros(i) - (i * 1e6)) < epsilon
        i += 0.5
