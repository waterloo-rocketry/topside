import topside as top
from topside.procedures.tests.testing_utils import NeverSatisfied


def test_immediate_condition():
    cond = top.Immediate()
    state = {}

    assert cond.satisfied() is True
    cond.update(state)
    assert cond.satisfied() is True


def test_immediate_equality():
    cond1 = top.Immediate()
    cond2 = top.Immediate()

    assert cond1 == cond2
    assert cond1 is not None


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


def test_wait_until_equality():
    cond1 = top.WaitUntil(100)
    cond2 = top.WaitUntil(100)
    cond3 = top.WaitUntil(200)

    assert cond1 == cond2
    assert cond1 != cond3

    assert cond1 != 100
    assert cond1 is not None


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


def test_equal_condition_equality():
    cond1 = top.Equal('p1', 100)
    cond2 = top.Equal('p1', 100)
    cond3 = top.Equal('p1', 100, 0)
    cond4 = top.Equal('p1', 200)
    cond5 = top.Equal('p2', 100)
    cond6 = top.Equal('p1', 100, 10)

    assert cond1 == cond2
    assert cond1 == cond3
    assert cond1 != cond4
    assert cond1 != cond5
    assert cond1 != cond6

    assert cond1 != 100
    assert cond1 is not None


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


def test_comparison_equality():
    c1 = top.Less('a1', 100)
    c2 = top.Less('a1', 100)  # same
    c3 = top.Less('b2', 100)  # different node
    c4 = top.Less('a1', 200)  # different reference
    c5 = top.Greater('a1', 100)  # different type

    assert c1 == c2
    assert c1 != c3
    assert c1 != c4
    assert c1 != c5


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


def test_nested_and_conditions():
    and_sat = top.And([top.Immediate(), top.And([top.Immediate(), top.Immediate()])])
    and_unsat = top.And([top.Immediate(), top.And([NeverSatisfied(), top.Immediate()])])

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


def test_and_equality():
    and_1 = top.And([top.Immediate(), top.Immediate()])
    and_2 = top.And([top.Immediate(), top.Immediate()])
    and_3 = top.And([NeverSatisfied(), top.Immediate()])

    assert and_1 == and_2
    assert and_1 != and_3

    assert and_1 != 10
    assert and_1 is not None


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


def test_nested_or_conditions():
    or_sat = top.Or([NeverSatisfied(), top.Or([top.Immediate(), NeverSatisfied()])])
    or_unsat = top.Or([NeverSatisfied(), top.Or([NeverSatisfied(), NeverSatisfied()])])

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


def test_or_equality():
    or_1 = top.Or([top.Immediate(), top.Immediate()])
    or_2 = top.Or([top.Immediate(), top.Immediate()])
    or_3 = top.Or([NeverSatisfied(), top.Immediate()])

    assert or_1 == or_2
    assert or_1 != or_3

    assert or_1 != 10
    assert or_1 is not None


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


def test_and_or_not_equal():
    and_cond = top.And([NeverSatisfied(), top.Immediate()])
    or_cond = top.Or([NeverSatisfied(), top.Immediate()])

    assert and_cond != or_cond


def test_string_representations():
    immediate_cond = top.Immediate()
    waitUntil_cond = top.WaitUntil(1000000)
    equal_cond = top.Equal('A1', 100)
    less_cond = top.Less('A2', 100)
    greater_cond = top.Greater('A3', 100)
    lessEqual_cond = top.LessEqual('A4', 100)
    greaterEqual_cond = top.GreaterEqual('A5', 100)
    and_cond = top.And([less_cond, greater_cond])
    or_cond = top.Or([lessEqual_cond, greaterEqual_cond])

    assert str(immediate_cond) == 'Condition always satisfied'
    assert str(waitUntil_cond) == 'Wait until 1 seconds'
    assert str(equal_cond) == 'A1 == 100'
    assert str(less_cond) == 'A2 < 100'
    assert str(greater_cond) == 'A3 > 100'
    assert str(lessEqual_cond) == 'A4 <= 100'
    assert str(greaterEqual_cond) == 'A5 >= 100'
    assert str(and_cond) == 'A2 < 100 and A3 > 100'
    assert str(or_cond) == 'A4 <= 100 or A5 >= 100'
