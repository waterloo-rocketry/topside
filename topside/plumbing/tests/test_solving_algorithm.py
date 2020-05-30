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


def test_step_errors():
    plumb = test.two_valve_setup(1, 1, 1, 1, 1, 1, 1, 1)

    fl = 102482.2
    with pytest.raises(exceptions.BadInputError) as err:
        plumb.step(fl)
    assert str(err.value) == f"timestep ({fl}) must be integer."

    too_low = 0
    with pytest.raises(exceptions.BadInputError) as err:
        plumb.step(too_low)
    assert str(err.value) ==\
        f"timestep ({too_low}) too low, must be greater than {utils.MIN_TIME_RES_MICROS} us."

    # This shouldn't raise an error, even though 10.0 is a float
    plumb.step(1000.0)


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

    solve_plumb = test.two_valve_setup(1, 1, 1, 1, 1, 1, 1, 1)
    solve_state = solve_plumb.solve()
    step_plumb = test.two_valve_setup(1, 1, 1, 1, 1, 1, 1, 1)
    step_state = step_plumb.step(steady_by)
    len_plumb = test.two_valve_setup(1, 1, 1, 1, 1, 1, 1, 1)
    solve_len = len(len_plumb.solve(return_resolution=len_plumb.time_res))
    test.validate_plumbing_engine(step_plumb, solve_plumb, steady_by, converged, 
                                  solve_state, step_state, solve_len, len_plumb.time_res)


def test_timeout():
    converged = {1: 33, 2: 33, 3: 33}

    big_teq = 100
    plumb = test.two_valve_setup(
        big_teq, big_teq, big_teq, big_teq, big_teq, big_teq, big_teq, big_teq)

    solve_state = plumb.solve(max_time=1)
    assert solve_state != converged

    plumb_long = test.two_valve_setup(
        big_teq, big_teq, big_teq, big_teq, big_teq, big_teq, big_teq, big_teq)
    solve_len = len(plumb_long.solve(max_time=1, return_resolution=plumb_long.time_res))
    assert solve_len == utils.s_to_micros(1)/plumb_long.time_res


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

    steady_by = utils.s_to_micros(1)
    converged = {1: 0, utils.ATM: 0}

    step_plumb = top.PlumbingEngine({'vent': pc}, mapping, pressures, default_states)
    step_state = step_plumb.step(1e6)

    solve_plumb = top.PlumbingEngine({'vent': pc}, mapping, pressures, default_states)
    solve_state = solve_plumb.solve()

    len_plumb = top.PlumbingEngine({'vent': pc}, mapping, pressures, default_states)
    solve_len = len(len_plumb.solve(return_resolution=len_plumb.time_res))
    test.validate_plumbing_engine(step_plumb, solve_plumb, steady_by, converged,
                                  solve_state, step_state, solve_len, len_plumb.time_res)


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
    default_states = {'valve': 'open'}
    step_plumb = top.PlumbingEngine({'valve': pc}, mapping, pressures, default_states)
    step_plumb.set_component_state('valve', 'closed')
    curr_nodes = step_plumb.nodes()
    step_plumb.step()
    assert curr_nodes == step_plumb.nodes()

    steady_by = utils.s_to_micros(1)
    converged = {1: 50, 2: 50}

    step_plumb.set_component_state('valve', 'open')
    step_state = step_plumb.step(1e6)

    solve_plumb = top.PlumbingEngine({'valve': pc}, mapping, pressures, default_states)
    solve_state = solve_plumb.solve()

    len_plumb = top.PlumbingEngine({'valve': pc}, mapping, pressures, default_states)
    solve_len = len(len_plumb.solve(return_resolution=len_plumb.time_res))
    test.validate_plumbing_engine(step_plumb, solve_plumb, steady_by, converged, 
                                  solve_state, step_state, solve_len, len_plumb.time_res)


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
    test.assert_no_change(plumb)


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
    test.assert_no_change(plumb)


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

    steady_by = utils.s_to_micros(1)
    converged = {1: 50, 2: 50}

    step_plumb = top.PlumbingEngine({'check': pc}, mapping, pressures, default_states)
    step_state = step_plumb.step(1e6)

    solve_plumb = top.PlumbingEngine({'check': pc}, mapping, pressures, default_states)
    solve_state = solve_plumb.solve()

    len_plumb = top.PlumbingEngine({'check': pc}, mapping, pressures, default_states)
    solve_len = len(len_plumb.solve(return_resolution=len_plumb.time_res))
    test.validate_plumbing_engine(step_plumb, solve_plumb, steady_by, converged, 
                                  solve_state, step_state, solve_len, len_plumb.time_res)


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

    steady_by = utils.s_to_micros(1)
    converged = {1: 50, 2: 50, 3: 0}

    step_plumb = top.PlumbingEngine({'three': pc}, mapping, pressures, {'three': 'open'})
    step_state = step_plumb.step(1e6)

    solve_plumb = top.PlumbingEngine({'three': pc}, mapping, pressures, {'three': 'open'})
    solve_state = solve_plumb.solve()

    len_plumb = top.PlumbingEngine({'three': pc}, mapping, pressures, {'three': 'open'})
    solve_len = len(len_plumb.solve(return_resolution=len_plumb.time_res))
    test.validate_plumbing_engine(step_plumb, solve_plumb, steady_by, converged, 
                                  solve_state, step_state, solve_len, len_plumb.time_res)
