import pytest

import topside as top
from topside.procedures.tests.testing_utils import NeverSatisfied


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


def test_and_one_condition():
    and_sat = top.And([top.Immediate()])
    and_unsat = top.And([NeverSatisfied()])

    assert and_sat.satisfied() is True
    assert and_unsat.satisfied() is False


def test_and_two_conditions():
    and_sat = top.And([top.Immediate(), top.Immediate()])
    and_unsat = top.And([NeverSatisfied(), top.Immediate()])

    assert and_sat.satisfied() is True
    assert and_unsat.satisfied() is False


def test_and_updates_subconditions():
    eq_cond = top.Equal('A1', 100)
    and_cond = top.And([eq_cond])

    state = {'pressures': {'A1': 100}}

    assert eq_cond.satisfied() is False
    assert and_cond.satisfied() is False
    and_cond.update(state)
    assert eq_cond.satisfied() is True
    assert and_cond.satisfied() is True


def test_and_requires_all_satisfied():
    eq_cond_1 = top.Equal('A1', 100)
    eq_cond_2 = top.Equal('A2', 100)
    and_cond = top.And([eq_cond_1, eq_cond_2])

    state = {'pressures': {'A1': 100, 'A2': 200}}

    assert eq_cond_1.satisfied() is False
    assert eq_cond_2.satisfied() is False
    assert and_cond.satisfied() is False
    and_cond.update(state)
    assert eq_cond_1.satisfied() is True
    assert eq_cond_2.satisfied() is False
    assert and_cond.satisfied() is False


def test_or_one_condition():
    or_sat = top.Or([top.Immediate()])
    or_unsat = top.Or([NeverSatisfied()])

    assert or_sat.satisfied() is True
    assert or_unsat.satisfied() is False


def test_or_two_conditions():
    or_sat = top.Or([top.Immediate(), NeverSatisfied()])
    or_unsat = top.Or([NeverSatisfied(), NeverSatisfied()])

    assert or_sat.satisfied() is True
    assert or_unsat.satisfied() is False


def test_or_updates_subconditions():
    eq_cond = top.Equal('A1', 100)
    or_cond = top.Or([eq_cond])

    state = {'pressures': {'A1': 100}}

    assert eq_cond.satisfied() is False
    assert or_cond.satisfied() is False
    or_cond.update(state)
    assert eq_cond.satisfied() is True
    assert or_cond.satisfied() is True


def test_or_requires_only_one_satisfied():
    eq_cond_1 = top.Equal('A1', 100)
    eq_cond_2 = top.Equal('A2', 100)
    or_cond = top.Or([eq_cond_1, eq_cond_2])

    state = {'pressures': {'A1': 100, 'A2': 200}}

    assert eq_cond_1.satisfied() is False
    assert eq_cond_2.satisfied() is False
    assert or_cond.satisfied() is False
    or_cond.update(state)
    assert eq_cond_1.satisfied() is True
    assert eq_cond_2.satisfied() is False
    assert or_cond.satisfied() is True


def test_nested_logic_works():
    eq_cond_1 = top.Equal('A1', 100)
    eq_cond_2 = top.Equal('A2', 100)
    eq_cond_3 = top.Equal('A3', 100)
    or_cond_1 = top.Or([eq_cond_1, eq_cond_2])
    or_cond_2 = top.Or([or_cond_1, eq_cond_3])

    state = {'pressures': {'A1': 100, 'A2': 200, 'A3': 300}}

    assert eq_cond_1.satisfied() is False
    assert eq_cond_2.satisfied() is False
    assert eq_cond_3.satisfied() is False
    assert or_cond_1.satisfied() is False
    assert or_cond_2.satisfied() is False
    or_cond_2.update(state)
    assert eq_cond_1.satisfied() is True
    assert eq_cond_2.satisfied() is False
    assert eq_cond_3.satisfied() is False
    assert or_cond_1.satisfied() is True
    assert or_cond_2.satisfied() is True
