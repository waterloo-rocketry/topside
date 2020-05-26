import pytest

import topside as top


def test_immediate_condition():
    cond = top.Immediate()
    state = {}

    assert cond.satisfied() is True
    cond.update(state)
    assert cond.satisfied() is True


def test_wait_until_condition_exact():
    cond = top.WaitUntil(100)
    state = {'time': 100}

    assert cond.satisfied() is False
    cond.update(state)
    assert cond.satisfied() is True


def test_wait_until_condition_before():
    cond = top.WaitUntil(100)
    state = {'time': 99}

    assert cond.satisfied() is False
    cond.update(state)
    assert cond.satisfied() is False


def test_wait_until_condition_after():
    cond = top.WaitUntil(100)
    state = {'time': 101}

    assert cond.satisfied() is False
    cond.update(state)
    assert cond.satisfied() is True


def test_custom_comparison_condition_requires_cond_fn():
    cond = top.Comparison('A1', 100)
    state = {'pressures': {'A1': 100}}
    cond.update(state)

    with pytest.raises(NotImplementedError):
        cond.satisfied()


def test_custom_comparison_condition():
    cond = top.Comparison('A1', 100, lambda x, y: abs(x - y) > 10)
    assert cond.satisfied() is False

    state1 = {'pressures': {'A1': 100}}
    cond.update(state1)
    assert cond.satisfied() is False

    state2 = {'pressures': {'A1': 111}}
    cond.update(state2)
    assert cond.satisfied() is True


def test_equal_condition_equal():
    cond = top.Equal('A1', 100)
    state = {'pressures': {'A1': 100}}

    assert cond.satisfied() is False
    cond.update(state)
    assert cond.satisfied() is True


def test_equal_condition_unequal():
    cond = top.Equal('A1', 100)
    state = {'pressures': {'A1': 101}}

    assert cond.satisfied() is False
    cond.update(state)
    assert cond.satisfied() is False


def test_equal_condition_with_eps():
    cond = top.Equal('A1', 100, 1)
    state = {'pressures': {'A1': 101}}

    assert cond.satisfied() is False
    cond.update(state)
    assert cond.satisfied() is True


def test_less_condition_equal():
    cond = top.Less('A1', 100)
    state = {'pressures': {'A1': 100}}

    assert cond.satisfied() is False
    cond.update(state)
    assert cond.satisfied() is False


def test_less_condition_greater():
    cond = top.Less('A1', 100)
    state = {'pressures': {'A1': 101}}

    assert cond.satisfied() is False
    cond.update(state)
    assert cond.satisfied() is False


def test_less_condition_less():
    cond = top.Less('A1', 100)
    state = {'pressures': {'A1': 99}}

    assert cond.satisfied() is False
    cond.update(state)
    assert cond.satisfied() is True


def test_less_equal_condition_equal():
    cond = top.LessEqual('A1', 100)
    state = {'pressures': {'A1': 100}}

    assert cond.satisfied() is False
    cond.update(state)
    assert cond.satisfied() is True


def test_less_equal_condition_greater():
    cond = top.LessEqual('A1', 100)
    state = {'pressures': {'A1': 101}}

    assert cond.satisfied() is False
    cond.update(state)
    assert cond.satisfied() is False


def test_less_equal_condition_less():
    cond = top.LessEqual('A1', 100)
    state = {'pressures': {'A1': 99}}

    assert cond.satisfied() is False
    cond.update(state)
    assert cond.satisfied() is True


def test_greater_condition_equal():
    cond = top.Greater('A1', 100)
    state = {'pressures': {'A1': 100}}

    assert cond.satisfied() is False
    cond.update(state)
    assert cond.satisfied() is False


def test_greater_condition_greater():
    cond = top.Greater('A1', 100)
    state = {'pressures': {'A1': 101}}

    assert cond.satisfied() is False
    cond.update(state)
    assert cond.satisfied() is True


def test_greater_condition_less():
    cond = top.Greater('A1', 100)
    state = {'pressures': {'A1': 99}}

    assert cond.satisfied() is False
    cond.update(state)
    assert cond.satisfied() is False


def test_greater_equal_condition_equal():
    cond = top.GreaterEqual('A1', 100)
    state = {'pressures': {'A1': 100}}

    assert cond.satisfied() is False
    cond.update(state)
    assert cond.satisfied() is True


def test_greater_equal_condition_greater():
    cond = top.GreaterEqual('A1', 100)
    state = {'pressures': {'A1': 101}}

    assert cond.satisfied() is False
    cond.update(state)
    assert cond.satisfied() is True


def test_greater_equal_condition_less():
    cond = top.GreaterEqual('A1', 100)
    state = {'pressures': {'A1': 99}}

    assert cond.satisfied() is False
    cond.update(state)
    assert cond.satisfied() is False
