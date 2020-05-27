import pytest

import datatest as dt

import topside as top
import topside.plumbing.exceptions as exceptions
import topside.plumbing.tests.testing_utils as test
import topside.plumbing.plumbing_utils as utils


def test_empty_engine():
    plumb = top.PlumbingEngine()
    with pytest.raises(exceptions.InvalidEngineError) as err:
        plumb.step(5)

    assert str(err.value) == "Step() cannot be called on an empty engine."


def test_invalid_engine():
    wrong_component_name = 'potato'
    pc1 = test.create_component(0, 0, 0, 0, 'valve1', 'A')
    pc2 = test.create_component(0, 0, 0, 0, 'valve2', 'B')

    component_mapping = {
        'valve1': {
            1: 1,
            2: 2
        },
        'valve2': {
            1: 2,
            2: 3
        }
    }

    pressures = {3: 100}
    default_states = {'valve1': 'closed', 'valve2': 'open'}
    plumb = top.PlumbingEngine(
        {wrong_component_name: pc1, 'valve2': pc2}, component_mapping, pressures, default_states)

    assert not plumb.is_valid()
    with pytest.raises(exceptions.InvalidEngineError) as err:
        plumb.step(5)
    assert str(err.value) == "Step() cannot be called on an invalid engine. Check for errors."


# Scneario based tests - these are meaty. Abbreviated descriptions come before the tests, but
# for an in depth description match the test number to what's on this doc:
# https://docs.google.com/document/d/1LwhcKiIn0qAECpmaBOFtkG4EBmUxXTU9uzSczCwrvpo/edit?usp=sharing
# This is the hackiest comment I've ever written


# A valve between a pressurized container and atmosphere is opened
def test_step_1():
    pass


def test_steady_1():
    pass


# The valve between two pressure vessels at different pressures is opened
def test_step_2():
    pass


def test_steady_2():
    pass


# The valve between a pressure vessel and atmosphere is closed
def test_step_3():
    pass


def test_steady_3():
    pass


# A pressure vessel is connected to the closed direction of a check valve
def test_step_4():
    pass


def test_steady_4():
    pass


# A pressure vessel is connected to the open direction of a check valve
def test_step_5():
    pass


def test_steady_5():
    pass


# Fluid flows through a three-way valve (one way open, one way closed)
def test_step_6():
    pass


def test_steady_6():
    pass