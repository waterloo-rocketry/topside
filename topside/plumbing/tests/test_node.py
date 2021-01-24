import pytest

import topside as top
import topside.plumbing.plumbing_utils as utils


def test_instantiate_node():
    expected_atm_node = top.instantiate_node(utils.ATM)
    atm_node = top.AtmNode()
    assert type(expected_atm_node) == type(atm_node)

    arbitrary_name = "name"
    expected_generic_node = top.instantiate_node(arbitrary_name)
    generic_node = top.GenericNode()
    assert type(expected_generic_node) == type(generic_node)


def test_generic_node():
    node = top.GenericNode()
    assert node.get_pressure() == 0
    assert not node.get_fixed()

    new_pressure = 100
    node.update_pressure(new_pressure)

    assert node.get_pressure() == new_pressure
    assert not node.get_fixed()

    node.update_fixed(True)
    assert node.get_pressure() == new_pressure
    assert node.get_fixed()

    # just make sure this doesn't error
    node.__str__()


def test_generic_equality():
    pressure = 10
    node = top.GenericNode(pressure, True)

    same_node = top.GenericNode(pressure, True)
    assert node == same_node

    diff_pressure = top.GenericNode(0, True)
    diff_fixed = top.GenericNode(pressure, False)
    assert node != diff_pressure
    assert node != diff_fixed

    diff_type = top.AtmNode()
    assert node != diff_type


def test_atm_node():
    node = top.AtmNode()
    assert node.get_pressure() == 0
    assert node.get_fixed()

    new_pressure = 100
    node.update_pressure(new_pressure)
    assert node.get_pressure() == 0
    assert node.get_fixed()

    node.update_fixed(False)
    assert node.get_pressure() == 0
    assert node.get_fixed()

    # make sure this doesn't error
    node.__str__()


def test_atm_equality():
    atm_node = top.AtmNode()
    another_atm_node = top.AtmNode()

    assert atm_node == another_atm_node

    almost_atm_node = top.GenericNode(0, True)
    assert atm_node != almost_atm_node
