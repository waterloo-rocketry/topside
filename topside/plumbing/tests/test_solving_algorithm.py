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

def test_closed_engine():
    plumb = test.two_valve_setup(utils.CLOSED, utils.CLOSED, utils.CLOSED,
                                 utils.CLOSED, utils.CLOSED, utils.CLOSED,
                                 utils.CLOSED, utils.CLOSED)
    state = plumb.step()
    assert state == {1: 0, 2: 0, 3: 100}
    state = plumb.solve()
    assert state == {1: 0, 2: 0, 3: 100}


# Scenario based tests - these are meaty. Abbreviated descriptions come before the tests, but
# for an in depth description match the test number to what's on this doc:
# https://docs.google.com/document/d/1LwhcKiIn0qAECpmaBOFtkG4EBmUxXTU9uzSczCwrvpo/edit?usp=sharing
# Each solve test has a value in micros, steady_by, which indicates the point at which it should be steady.
# To test solve(), its result is compared against that of plumb.step(steady_by). Solve must converge
# within 2*steady_by seconds.


def test_misc_engine():
    steady_by = utils.s_to_micros(1)
    converged = {1: 33, 2: 33, 3: 33}

    plumb = test.two_valve_setup(1, 1, 1, 1, 1, 1, 1, 1)
    solve_state = plumb.solve()
    plumb = test.two_valve_setup(1, 1, 1, 1, 1, 1, 1, 1)
    step_state = plumb.step(steady_by)
    with dt.accepted.tolerance(test.SOLVE_TOL):
        dt.validate(solve_state, step_state)

    with dt.accepted.tolerance(5):
        dt.validate(solve_state, converged)

    plumb = test.two_valve_setup(1, 1, 1, 1, 1, 1, 1, 1)
    solve_len = plumb.solve(return_resolution=plumb.time_resolution)
    assert len(solve_len) < 2* steady_by / plumb.time_resolution


# A valve between a pressurized container and atmosphere is opened
def test_1():
    pc = test.create_component(1, 1, 1, 1, 'vent', 'A')
    mapping = {
        'vent': {
            1: 1,
            2: utils.ATM
        }
    }
    pressures = {1: 100}
    default_states = {'vent': 'open'}
    plumb = top.PlumbingEngine({'vent': pc}, mapping, pressures, default_states)

    steady_by = utils.s_to_micros(1)
    converged = {1: 0, utils.ATM: 0}

    step_state = plumb.step(1000000)

    plumb.set_pressure(1, 100)
    solve_state = plumb.solve()

    with dt.accepted.tolerance(test.SOLVE_TOL):
        dt.validate(solve_state, step_state)

    with dt.accepted.tolerance(5):
        dt.validate(solve_state, converged)

    plumb.set_pressure(1, 100)
    solve_len = plumb.solve(return_resolution=plumb.time_resolution)
    assert len(solve_len) < 2* steady_by / plumb.time_resolution

# The valve between two pressure vessels at different pressures is opened
def test_2():
    pc = test.create_component(1, 1, utils.CLOSED, utils.CLOSED, 'valve', 'A')
    mapping = {
        'valve': {
            1: 1,
            2: 2
        }
    }
    pressures = {1: 100}
    default_states = {'valve': 'closed'}
    plumb = top.PlumbingEngine({'valve': pc}, mapping, pressures, default_states)
    curr_nodes = plumb.nodes()
    plumb.step()
    assert curr_nodes == plumb.nodes()

    steady_by = utils.s_to_micros(1)
    converged = {1: 50, 2: 50}

    plumb.set_component_state('valve', 'open')
    step_state = plumb.step(1000000)

    plumb.set_pressure(1, 100)
    plumb.set_pressure(2, 0)
    solve_state = plumb.solve()

    with dt.accepted.tolerance(test.SOLVE_TOL):
        dt.validate(solve_state, step_state)

    with dt.accepted.tolerance(5):
        dt.validate(solve_state, converged)

    plumb.set_pressure(1, 100)
    plumb.set_pressure(2, 0)
    solve_len = plumb.solve(return_resolution=plumb.time_resolution)
    assert len(solve_len) < 2 * steady_by / plumb.time_resolution


# The valve between a pressure vessel and atmosphere is closed
def test_3():
    pc = test.create_component(1, 1, utils.CLOSED, utils.CLOSED, 'vent', 'A')
    mapping = {
        'vent': {
            1: 1,
            2: utils.ATM
        }
    }
    pressures = {1: 100}
    default_states = {'vent': 'closed'}
    plumb = top.PlumbingEngine({'vent': pc}, mapping, pressures, default_states)
    curr_nodes = plumb.nodes()
    plumb.step()
    assert curr_nodes == plumb.nodes()
    plumb.solve()
    assert curr_nodes == plumb.nodes()

    min_iter = 2
    solve_state = plumb.solve(return_resolution=plumb.time_resolution)
    assert len(solve_state) == min_iter


# A pressure vessel is connected to the closed direction of a check valve
def test_4():
    pc = test.create_component(1, utils.CLOSED, utils.CLOSED, utils.CLOSED, 'check', 'A')
    mapping = {
        'check': {
            1: 1,
            2: 2
        }
    }
    pressures = {1: 100}
    default_states = {'check': 'closed'}
    plumb = top.PlumbingEngine({'check': pc}, mapping, pressures, default_states)
    curr_nodes = plumb.nodes()
    plumb.step()
    assert curr_nodes == plumb.nodes()
    plumb.solve()
    assert curr_nodes == plumb.nodes()

    min_iter = 2
    solve_state = plumb.solve(return_resolution=plumb.time_resolution)
    assert len(solve_state) == min_iter


# A pressure vessel is connected to the open direction of a check valve
def test_5():
    pc = test.create_component(1, utils.CLOSED, utils.CLOSED, utils.CLOSED, 'check', 'A')
    mapping = {
        'check': {
            1: 1,
            2: 2
        }
    }
    pressures = {1: 100}
    default_states = {'check': 'open'}
    plumb = top.PlumbingEngine({'check': pc}, mapping, pressures, default_states)

    steady_by = utils.s_to_micros(1)
    converged = {1: 50, 2: 50}

    step_state = plumb.step(1000000)

    plumb.set_pressure(1, 100)
    plumb.set_pressure(2, 0)
    solve_state = plumb.solve()

    with dt.accepted.tolerance(test.SOLVE_TOL):
        dt.validate(solve_state, step_state)

    with dt.accepted.tolerance(5):
        dt.validate(solve_state, converged)

    plumb.set_pressure(1, 100)
    plumb.set_pressure(2, 0)
    solve_len = plumb.solve(return_resolution=plumb.time_resolution)
    assert len(solve_len) < 2 * steady_by / plumb.time_resolution


# Fluid flows through a three-way valve (one way open, one way closed)
def test_6():
    states = {
        'open': {
            (1, 2, 'A1'): 1,
            (2, 1, 'A2'): 1,
            (1, 3, 'B1'): utils.CLOSED,
            (3, 1, 'B2'): utils.CLOSED
        }
    }
    edges = [(1, 2, 'A1'), (2, 1, 'A2'), (1, 3, 'B1'), (3, 1, 'B2')]
    pc = top.PlumbingComponent('three', states, edges)
    mapping = {
        'three': {
            1: 1,
            2: 2,
            3: 3
        }
    }
    pressures = {
        1: 100,
        2: 0,
        3: 0
    }
    plumb = top.PlumbingEngine({'three': pc}, mapping, pressures, {'three': 'open'})

    steady_by = utils.s_to_micros(1)
    converged = {1: 50, 2: 50, 3: 0}

    step_state = plumb.step(1000000)

    plumb.set_pressure(1, 100)
    plumb.set_pressure(2, 0)
    solve_state = plumb.solve()

    with dt.accepted.tolerance(test.SOLVE_TOL):
        dt.validate(solve_state, step_state)

    with dt.accepted.tolerance(5):
        dt.validate(solve_state, converged)

    plumb.set_pressure(1, 100)
    plumb.set_pressure(2, 0)
    solve_len = plumb.solve(return_resolution=plumb.time_resolution)
    assert len(solve_len) < 2 * steady_by / plumb.time_resolution
