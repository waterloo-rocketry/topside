import pytest

import topside as top
import topside.plumbing.invalid_reasons as invalid
import topside.plumbing.exceptions as exceptions
import topside.plumbing.tests.testing_utils as test
import topside.plumbing.plumbing_utils as utils


def test_add_to_empty():
    plumb = top.PlumbingEngine()
    pc = test.create_component(2, utils.CLOSED, 0, 0, 'valve', 'A')

    mapping = {
        1: 1,
        2: 2
    }

    plumb.add_component(pc, mapping, 'open', {1: (20, False)})

    assert plumb.is_valid()
    assert plumb.time_res == utils.DEFAULT_TIME_RESOLUTION_MICROS
    assert plumb.edges() == [
        (1, 2, 'valve.A1', {'FC': utils.teq_to_FC(utils.s_to_micros(2))}),
        (2, 1, 'valve.A2', {'FC': 0})
    ]
    assert plumb.nodes() == [
        (1, {'body': top.GenericNode(20)}),
        (2, {'body': top.GenericNode(0)})
    ]
    assert plumb.current_state('valve') == 'open'


def test_add_component():
    plumb = test.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED, 0.5, 0.2, 10, utils.CLOSED)

    pc = test.create_component(0, 0, 0, 1, 'valve3', 'C')
    mapping = {
        1: 3,
        2: 4
    }

    plumb.add_component(pc, mapping, 'closed', {4: (50, False)})

    assert plumb.is_valid()
    assert plumb.time_res == int(utils.s_to_micros(0.2) / utils.DEFAULT_RESOLUTION_SCALE)
    assert plumb.edges() == [
        (1, 2, 'valve1.A1', {'FC': utils.teq_to_FC(utils.s_to_micros(10))}),
        (2, 1, 'valve1.A2', {'FC': 0}),
        (2, 3, 'valve2.B1', {'FC': utils.teq_to_FC(utils.s_to_micros(0.5))}),
        (3, 2, 'valve2.B2', {'FC': utils.teq_to_FC(utils.s_to_micros(0.2))}),
        (3, 4, 'valve3.C1', {'FC': utils.teq_to_FC(0)}),
        (4, 3, 'valve3.C2', {'FC': utils.teq_to_FC(utils.s_to_micros(1))})
    ]
    assert plumb.nodes() == [
        (1, {'body': top.GenericNode(0)}),
        (2, {'body': top.GenericNode(0)}),
        (3, {'body': top.GenericNode(100)}),
        (4, {'body': top.GenericNode(50)})
    ]
    assert plumb.current_state('valve1') == 'closed'
    assert plumb.current_state('valve2') == 'open'
    assert plumb.current_state('valve3') == 'closed'


def test_add_component_errors():
    plumb = test.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED, 0.5, 0.2, 10, utils.CLOSED)

    name = 'valve3'
    wrong_node = 3
    right_node = 2
    pc = test.create_component(0, 0, 0, 1, name, 'C')
    mapping = {
        1: 3,
        wrong_node: 4
    }

    with pytest.raises(exceptions.BadInputError) as err:
        plumb.add_component(pc, mapping, 'closed', {4: (50, False)})
    assert str(err.value) ==\
        f"Component '{name}', node {right_node} not found in mapping dict."


def test_add_invalid_component():
    plumb = test.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED, 0.5, 0.2, 10, utils.CLOSED)

    wrong_node = 5
    pc_states = {
        'open': {
            (1, wrong_node, 'A1'): 0,
            (2, 1, 'A2'): 0
        },
        'closed': {
            (1, 2, 'A1'): 0,
            (2, 1, 'A2'): 0
        }
    }
    pc_edges = [(1, 2, 'A1'), (2, 1, 'A2')]
    invalid_pc = top.PlumbingComponent('valve', pc_states, pc_edges)

    assert not invalid_pc.is_valid()

    with pytest.raises(exceptions.BadInputError) as err:
        plumb.add_component(invalid_pc, {1: 3, 2: 4}, 'open')
    assert str(err.value) == "Component not valid; all errors must be resolved before loading in."


def test_reset_added_component():
    plumb = test.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED, 0.5, 0.2, 10, utils.CLOSED)

    pc = test.create_component(0, 0, 0, 1, 'valve3', 'C')
    mapping = {
        1: 3,
        2: 4
    }

    plumb.add_component(pc, mapping, 'closed', {4: (50, False)})
    plumb.reset(True)

    plumb_initial = test.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED, 0.5, 0.2, 10, utils.CLOSED)

    assert plumb.time == 0
    assert plumb.is_valid()
    assert plumb.time_res == plumb_initial.time_res
    assert plumb.edges() == plumb_initial.edges()
    assert plumb.nodes() == plumb_initial.nodes()
    assert plumb.current_state() == plumb_initial.current_state()


def test_reset_removed_component():
    plumb = test.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED, 0.5, 0.2, 10, utils.CLOSED)

    plumb.remove_component('valve2')
    plumb.reset(True)

    plumb_initial = test.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED, 0.5, 0.2, 10, utils.CLOSED)

    assert plumb.time == 0
    assert plumb.is_valid()
    assert plumb.time_res == plumb_initial.time_res
    assert plumb.edges() == plumb_initial.edges()
    assert plumb.nodes() == plumb_initial.nodes()
    assert plumb.current_state() == plumb_initial.current_state()


def test_reset_component_state():
    plumb = test.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED, 0.5, 0.2, 10, utils.CLOSED)

    plumb.set_component_state('valve1', 'open')
    plumb.reset()

    plumb_initial = test.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED, 0.5, 0.2, 10, utils.CLOSED)

    assert plumb.time == 0
    assert plumb.is_valid()
    assert plumb.time_res == plumb_initial.time_res
    assert plumb.edges() == plumb_initial.edges()
    assert plumb.nodes() == plumb_initial.nodes()
    assert plumb.current_state() == plumb_initial.current_state()


def test_reset_pressure():
    plumb = test.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED, 0.5, 0.2, 10, utils.CLOSED)

    plumb.set_pressure(2, 150)
    plumb.reset()

    plumb_initial = test.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED, 0.5, 0.2, 10, utils.CLOSED)

    assert plumb.time == 0
    assert plumb.is_valid()
    assert plumb.time_res == plumb_initial.time_res
    assert plumb.edges() == plumb_initial.edges()
    assert plumb.nodes() == plumb_initial.nodes()
    assert plumb.current_state() == plumb_initial.current_state()


def test_reset_step_and_solve():
    plumb = test.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED, 0.5, 0.2, 10, utils.CLOSED)

    plumb.step()
    plumb.solve()
    plumb.reset()

    plumb_initial = test.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED, 0.5, 0.2, 10, utils.CLOSED)

    assert plumb.time == 0
    assert plumb.is_valid()
    assert plumb.time_res == plumb_initial.time_res
    assert plumb.edges() == plumb_initial.edges()
    assert plumb.nodes() == plumb_initial.nodes()
    assert plumb.current_state() == plumb_initial.current_state()


def test_reset_keep_component():
    plumb = test.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED, 0.5, 0.2, 10, utils.CLOSED)

    pc = test.create_component(0, 0, 0, 1, 'valve3', 'C')
    mapping = {
        1: 3,
        2: 4
    }

    plumb.add_component(pc, mapping, 'closed', {4: (50, False)})
    plumb.remove_component('valve2')
    plumb.reset()

    assert plumb.time == 0
    assert plumb.is_valid()
    assert plumb.time_res == int(utils.s_to_micros(0.2) / utils.DEFAULT_RESOLUTION_SCALE)
    assert plumb.edges() == [
        (1, 2, 'valve1.A1', {'FC': utils.teq_to_FC(utils.s_to_micros(10))}),
        (2, 1, 'valve1.A2', {'FC': 0}),
        (3, 4, 'valve3.C1', {'FC': utils.teq_to_FC(0)}),
        (4, 3, 'valve3.C2', {'FC': utils.teq_to_FC(utils.s_to_micros(1))})
    ]
    assert plumb.nodes() == [
        (1, {'body': top.GenericNode(0)}),
        (2, {'body': top.GenericNode(0)}),
        (3, {'body': top.GenericNode(100)}),
        (4, {'body': top.GenericNode(0)})
    ]
    assert plumb.current_state('valve1') == 'closed'
    assert plumb.current_state('valve3') == 'closed'


def test_reset_fixed_pressure():
    plumb = test.two_valve_setup_fixed(
        0.5, 0.2, 10, utils.CLOSED, 0.5, 0.2, 10, utils.CLOSED)

    plumb.set_pressure(2, 150)
    plumb.reset()

    plumb_initial = test.two_valve_setup_fixed(
        0.5, 0.2, 10, utils.CLOSED, 0.5, 0.2, 10, utils.CLOSED)

    assert plumb.time == 0
    assert plumb.is_valid()
    assert plumb.time_res == plumb_initial.time_res
    assert plumb.edges() == plumb_initial.edges()
    assert plumb.nodes() == plumb_initial.nodes()
    assert plumb.current_state() == plumb_initial.current_state()
    assert plumb.fixed_pressures == plumb_initial.fixed_pressures


def test_integration_reset():
    plumb = test.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED, 0.5, 0.2, 10, utils.CLOSED)

    pc = test.create_component(0, 0, 0, 1, 'valve3', 'C')
    mapping = {
        1: 3,
        2: 4
    }

    plumb.remove_component('valve2')
    plumb.add_component(pc, mapping, 'closed', {4: (50, False)})
    plumb.set_component_state('valve1', 'open')
    plumb.set_pressure(3, 150)
    plumb.reset(True)

    plumb_initial = test.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED, 0.5, 0.2, 10, utils.CLOSED)

    assert plumb.time == 0
    assert plumb.is_valid()
    assert plumb.time_res == plumb_initial.time_res
    assert plumb.edges() == plumb_initial.edges()
    assert plumb.nodes() == plumb_initial.nodes()
    assert plumb.current_state() == plumb_initial.current_state()


def test_reset_integration_and_keep_component():
    plumb = test.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED, 0.5, 0.2, 10, utils.CLOSED)

    pc = test.create_component(0, 0, 0, 1, 'valve3', 'C')
    mapping = {
        1: 3,
        2: 4
    }

    plumb.remove_component('valve2')
    plumb.add_component(pc, mapping, 'closed', {4: (50, False)})
    plumb.set_component_state('valve1', 'open')
    plumb.set_pressure(3, 150)
    plumb.reset()

    assert plumb.time == 0
    assert plumb.is_valid()
    assert plumb.time_res == int(utils.s_to_micros(0.2) / utils.DEFAULT_RESOLUTION_SCALE)
    assert plumb.edges() == [
        (1, 2, 'valve1.A1', {'FC': utils.teq_to_FC(utils.s_to_micros(10))}),
        (2, 1, 'valve1.A2', {'FC': 0}),
        (3, 4, 'valve3.C1', {'FC': utils.teq_to_FC(0)}),
        (4, 3, 'valve3.C2', {'FC': utils.teq_to_FC(utils.s_to_micros(1))})
    ]
    assert plumb.nodes() == [
        (1, {'body': top.GenericNode(0)}),
        (2, {'body': top.GenericNode(0)}),
        (3, {'body': top.GenericNode(100)}),
        (4, {'body': top.GenericNode(0)})
    ]
    assert plumb.current_state('valve1') == 'closed'
    assert plumb.current_state('valve3') == 'closed'


def test_remove_component():
    plumb = test.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED, 0.5, 0.2, 10, utils.CLOSED)
    plumb.remove_component('valve2')

    assert plumb.is_valid()
    assert plumb.time_res == int(utils.s_to_micros(0.2) / utils.DEFAULT_RESOLUTION_SCALE)
    assert plumb.edges() == [
        (1, 2, 'valve1.A1', {'FC': utils.teq_to_FC(utils.s_to_micros(10))}),
        (2, 1, 'valve1.A2', {'FC': 0}),
    ]
    assert plumb.nodes() == [
        (1, {'body': top.GenericNode(0)}),
        (2, {'body': top.GenericNode(0)}),
    ]
    assert plumb.current_state('valve1') == 'closed'


def test_add_remove():
    old_lowest_teq = 0.2
    plumb = test.two_valve_setup(
        0.5, old_lowest_teq, 10, utils.CLOSED, 0.5, old_lowest_teq, 10,
        utils.CLOSED)

    new_lowest_teq = 0.1
    pc = test.create_component(0, 0, 0, new_lowest_teq, 'valve3', 'C')
    mapping = {
        1: 3,
        2: 4
    }

    plumb.add_component(pc, mapping, 'closed', {4: (50, False)})

    assert plumb.time_res ==\
        int(utils.s_to_micros(new_lowest_teq) / utils.DEFAULT_RESOLUTION_SCALE)

    plumb.remove_component('valve3')

    assert plumb.is_valid()
    assert plumb.time_res ==\
        int(utils.s_to_micros(old_lowest_teq) / utils.DEFAULT_RESOLUTION_SCALE)
    assert plumb.edges() == [
        (1, 2, 'valve1.A1', {'FC': utils.teq_to_FC(utils.s_to_micros(10))}),
        (2, 1, 'valve1.A2', {'FC': 0}),
        (2, 3, 'valve2.B1', {'FC': utils.teq_to_FC(utils.s_to_micros(0.5))}),
        (3, 2, 'valve2.B2', {'FC': utils.teq_to_FC(utils.s_to_micros(0.2))}),
    ]
    assert plumb.nodes() == [
        (1, {'body': top.GenericNode(0)}),
        (2, {'body': top.GenericNode(0)}),
        (3, {'body': top.GenericNode(100)}),
    ]
    assert plumb.current_state('valve1') == 'closed'
    assert plumb.current_state('valve2') == 'open'


def test_remove_nonexistent_component():
    plumb = test.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED, 0.5, 0.2, 10, utils.CLOSED)
    nonexistent_component = 'potato'

    with pytest.raises(exceptions.BadInputError) as err:
        plumb.remove_component(nonexistent_component)
    assert str(err.value) ==\
        f"Component with name {nonexistent_component} not found in component dict."


def test_remove_add_errors():
    plumb = test.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED, 0.5, 0.2, 10, utils.CLOSED)

    name = 'valve3'
    wrong_node = 3
    right_node = 2
    pc = test.create_component(0, 0, 0, 1, name, 'C')
    mapping = {
        1: 3,
        wrong_node: 4
    }

    with pytest.raises(exceptions.BadInputError) as err:
        plumb.add_component(pc, mapping, 'closed', {4: (50, False)})
    assert str(err.value) ==\
        f"Component '{name}', node {right_node} not found in mapping dict."

    plumb.remove_component(name)

    assert plumb.is_valid()
    assert plumb.time_res == int(utils.s_to_micros(0.2) / utils.DEFAULT_RESOLUTION_SCALE)
    assert plumb.edges() == [
        (1, 2, 'valve1.A1', {'FC': utils.teq_to_FC(utils.s_to_micros(10))}),
        (2, 1, 'valve1.A2', {'FC': 0}),
        (2, 3, 'valve2.B1', {'FC': utils.teq_to_FC(utils.s_to_micros(0.5))}),
        (3, 2, 'valve2.B2', {'FC': utils.teq_to_FC(utils.s_to_micros(0.2))}),
    ]
    assert plumb.nodes() == [
        (1, {'body': top.GenericNode(0)}),
        (2, {'body': top.GenericNode(0)}),
        (3, {'body': top.GenericNode(100)}),
    ]
    assert plumb.current_state('valve1') == 'closed'
    assert plumb.current_state('valve2') == 'open'


def test_remove_errors_wrong_component_name():
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

    pressures = {3: (100, False)}
    default_states = {'valve1': 'closed', 'valve2': 'open'}
    plumb = top.PlumbingEngine(
        {wrong_component_name: pc1, 'valve2': pc2}, component_mapping, pressures, default_states)

    assert not plumb.is_valid()
    assert len(plumb.errors()) == 2

    error1 = invalid.InvalidComponentName(
        f"Component with name '{wrong_component_name}' not found in mapping dict.",
        wrong_component_name)

    error2 = invalid.InvalidComponentName(
        f"Component '{wrong_component_name}' state not found in initial states dict.",
        wrong_component_name)

    assert error1 in plumb.errors()
    assert error2 in plumb.errors()

    plumb.remove_component(wrong_component_name)

    assert plumb.is_valid()
    assert plumb.time_res == int(utils.s_to_micros(0.2) / utils.DEFAULT_RESOLUTION_SCALE)
    assert plumb.edges() == [
        (2, 3, 'valve2.B1', {'FC': utils.teq_to_FC(utils.s_to_micros(0))}),
        (3, 2, 'valve2.B2', {'FC': utils.teq_to_FC(utils.s_to_micros(0))}),
    ]
    assert plumb.nodes() == [
        (2, {'body': top.GenericNode(0)}),
        (3, {'body': top.GenericNode(100)}),
    ]
    assert plumb.current_state('valve2') == 'open'


def test_reverse_orientation():
    plumb = test.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED, 0.5, 0.2, 10, utils.CLOSED)
    plumb.reverse_orientation('valve1')

    assert plumb.is_valid()
    assert plumb.time_res == int(utils.s_to_micros(0.2) / utils.DEFAULT_RESOLUTION_SCALE)
    assert plumb.edges() == [
        (1, 2, 'valve1.A1', {'FC': 0}),
        (2, 1, 'valve1.A2', {'FC': utils.teq_to_FC(utils.s_to_micros(10))}),
        (2, 3, 'valve2.B1', {'FC': utils.teq_to_FC(utils.s_to_micros(0.5))}),
        (3, 2, 'valve2.B2', {'FC': utils.teq_to_FC(utils.s_to_micros(0.2))})
    ]
    assert plumb.nodes() == [
        (1, {'body': top.GenericNode(0)}),
        (2, {'body': top.GenericNode(0)}),
        (3, {'body': top.GenericNode(100)}),
    ]
    assert plumb.current_state('valve1') == 'closed'
    assert plumb.current_state('valve2') == 'open'


def test_reverse_orientation_wrong_component():
    wrong_name = 'potato'
    plumb = test.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED, 0.5, 0.2, 10, utils.CLOSED)

    with pytest.raises(exceptions.BadInputError) as err:
        plumb.reverse_orientation(wrong_name)
    assert str(err.value) == f"Component '{wrong_name}' not found in component dict."


def test_reverse_orientation_three_edges():
    pc_states = {
        'open': {
            (1, 2, 'A1'): 5,
            (2, 1, 'A2'): 0,
            (1, 3, 'B1'): 3,
            (3, 1, 'B2'): 0,
            (2, 3, 'C1'): 4,
            (3, 2, 'C2'): 5
        }
    }
    pc_edges = [(1, 2, 'A1'), (2, 1, 'A2'), (1, 3, 'B1'), (3, 1, 'B2'), (2, 3, 'C1'), (3, 2, 'C2')]
    pc = top.PlumbingComponent('threeway', pc_states, pc_edges)

    plumb = test.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED, 0.5, 0.2, 10, utils.CLOSED)

    mapping = {
        1: 3,
        2: 4,
        3: 5
    }
    plumb.add_component(pc, mapping, 'open')

    with pytest.raises(exceptions.InvalidComponentError) as err:
        plumb.reverse_orientation('threeway')
    assert str(err.value) == "Component must only have two edges to be automatically reversed.\n" +\
        "Consider adjusting direction manually."


def test_set_pressure():
    plumb = test.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED, 0.5, 0.2, 10, utils.CLOSED)
    pc = test.create_component(0, 0, 0, 1, 'valve3', 'C')
    mapping = {
        1: 3,
        2: 4
    }
    plumb.add_component(pc, mapping, 'closed', {4: (50, False)})

    plumb.set_pressure(1, 200)
    plumb.set_pressure(2, 7000)

    assert plumb.nodes() == [
        (1, {'body': top.GenericNode(200)}),
        (2, {'body': top.GenericNode(7000)}),
        (3, {'body': top.GenericNode(100)}),
        (4, {'body': top.GenericNode(50)})
    ]

    plumb.set_pressure(4, 10)
    plumb.set_pressure(1, 0)

    assert plumb.nodes() == [
        (1, {'body': top.GenericNode(0)}),
        (2, {'body': top.GenericNode(7000)}),
        (3, {'body': top.GenericNode(100)}),
        (4, {'body': top.GenericNode(10)})
    ]


def test_set_pressure_errors():
    plumb = test.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED, 0.5, 0.2, 10, utils.CLOSED)

    pc = test.create_component(0, 0, 0, 1, 'valve3', 'C')
    mapping = {
        1: 3,
        2: 4
    }
    plumb.add_component(pc, mapping, 'closed', {4: (50, False)})

    pc_vent = test.create_component(0, 0, 0, 0, 'vent', 'D')
    mapping_vent = {
        1: 4,
        2: utils.ATM
    }
    plumb.add_component(pc_vent, mapping_vent, 'closed')

    negative_pressure = -20
    not_a_number = 'potato'
    with pytest.raises(exceptions.BadInputError) as err:
        plumb.set_pressure(4, negative_pressure)
    assert str(err.value) == f"Negative pressure {negative_pressure} not allowed."

    with pytest.raises(exceptions.BadInputError) as err:
        plumb.set_pressure(4, not_a_number)
    assert str(err.value) == f"Pressure {not_a_number} must be a number."

    assert plumb.nodes() == [
        (1, {'body': top.GenericNode(0)}),
        (2, {'body': top.GenericNode(0)}),
        (3, {'body': top.GenericNode(100)}),
        (4, {'body': top.GenericNode(50)}),
        (utils.ATM, {'body': top.AtmNode()})
    ]

    nonexistent_node = 5
    with pytest.raises(exceptions.BadInputError) as err:
        plumb.set_pressure(nonexistent_node, 100)
    assert str(err.value) == f"Node {nonexistent_node} not found in graph."

    plumb.set_pressure(4, 100)
    assert plumb.nodes() == [
        (1, {'body': top.GenericNode(0)}),
        (2, {'body': top.GenericNode(0)}),
        (3, {'body': top.GenericNode(100)}),
        (4, {'body': top.GenericNode(100)}),
        (utils.ATM, {'body': top.AtmNode()})
    ]

    with pytest.raises(exceptions.BadInputError) as err:
        plumb.set_pressure(utils.ATM, 100)
    assert str(err.value) == f"Pressure for atmosphere node ({utils.ATM}) must be 0."


def test_set_teq():
    old_lowest_teq = 0.2
    plumb = test.two_valve_setup(
        0.5, old_lowest_teq, 10, utils.CLOSED, 0.5, old_lowest_teq, 10,
        utils.CLOSED)

    new_lowest_teq = 0.1
    which_edge = {
        'closed': {
            (2, 1, 'A2'): new_lowest_teq,
            (1, 2, 'A1'): 7
        },
        'open': {
            (1, 2, 'A1'): 1
        }
    }

    plumb.set_teq('valve1', which_edge)

    assert plumb.time_res ==\
        int(utils.s_to_micros(new_lowest_teq) / utils.DEFAULT_RESOLUTION_SCALE)
    assert plumb.edges() == [
        (1, 2, 'valve1.A1', {'FC': utils.teq_to_FC(utils.s_to_micros(7))}),
        (2, 1, 'valve1.A2', {'FC': utils.teq_to_FC(utils.s_to_micros(new_lowest_teq))}),
        (2, 3, 'valve2.B1', {'FC': utils.teq_to_FC(utils.s_to_micros(0.5))}),
        (3, 2, 'valve2.B2', {'FC': utils.teq_to_FC(utils.s_to_micros(0.2))})
    ]
    assert plumb.component_dict['valve1'].states == {
        'open': {
            (1, 2, 'A1'): utils.teq_to_FC(utils.s_to_micros(1)),
            (2, 1, 'A2'): utils.teq_to_FC(utils.s_to_micros(old_lowest_teq))
        },
        'closed': {
            (1, 2, 'A1'): utils.teq_to_FC(utils.s_to_micros(7)),
            (2, 1, 'A2'): utils.teq_to_FC(utils.s_to_micros(new_lowest_teq))
        }
    }


def test_set_teq_errors():
    plumb = test.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED, 0.5, 0.2, 10, utils.CLOSED)

    which_edge = {
        'closed': {
            (2, 1, 'A2'): 1,
            (1, 2, 'A1'): 7
        },
        'open': {
            (1, 2, 'A1'): 1
        }
    }

    wrong_name = 'potato'
    teq_too_low = utils.micros_to_s(utils.TEQ_MIN/2)
    bad_teq = {
        'closed': {
            (2, 1, 'A2'): teq_too_low,
            (1, 2, 'A1'): 7
        },
        'open': {
            (1, 2, 'A1'): 1
        }
    }

    bad_state = {
        'closed': {
            (2, 1, 'A2'): 1,
            (1, 2, 'A1'): 7
        },
        wrong_name: {
            (1, 2, 'A1'): 1
        }
    }

    bad_key = {
        'closed': {
            (2, 1, wrong_name): 1,
            (1, 2, 'A1'): 7
        },
        'open': {
            (1, 2, 'A1'): 1
        }
    }

    with pytest.raises(exceptions.BadInputError) as err:
        plumb.set_teq('valve1', bad_teq)
    assert str(err.value) == f"Provided teq {teq_too_low} (component 'valve1', state 'closed'," +\
        f" edge (2, 1, 'A2')) too low. Minimum teq is {utils.micros_to_s(utils.TEQ_MIN)}s."

    with pytest.raises(exceptions.BadInputError) as err:
        plumb.set_teq(wrong_name, which_edge)
    assert str(err.value) == f"Component name '{wrong_name}' not found in component dict."

    with pytest.raises(exceptions.BadInputError) as err:
        plumb.set_teq('valve1', bad_key)
    assert str(err.value) == f"State 'closed', edge (2, 1, '{wrong_name}') not found in" +\
        " component valve1's states dict."

    with pytest.raises(exceptions.BadInputError) as err:
        plumb.set_teq('valve1', bad_state)
    assert str(err.value) == f"State '{wrong_name}' not found in component valve1's states dict."


def test_toggle_listing():
    plumb = test.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED, 0.5, 0.2, 10, utils.CLOSED)

    pc_states = {
        'open': {
            (1, 2, 'A1'): 0,
            (2, 1, 'A2'): 0
        }
    }
    pc_edges = [(1, 2, 'A1'), (2, 1, 'A2')]

    pc = top.PlumbingComponent('tank', pc_states, pc_edges)

    mapping = {1: 3, 2: 4}
    plumb.add_component(pc, mapping, 'open')

    toggles = plumb.list_toggles()

    assert len(toggles) == 2
    assert 'valve1' in toggles
    assert 'valve2' in toggles
    assert 'tank' not in toggles


def test_unfix_node():
    plumb = test.two_valve_setup_fixed(1, 1, 1, 1, 1, 1, 1, 1)

    assert plumb.fixed_pressures == {3: 100}

    plumb.set_pressure(3, 100, False)

    assert plumb.fixed_pressures == {}


def test_fix_node():
    plumb = test.two_valve_setup(1, 1, 1, 1, 1, 1, 1, 1)

    assert plumb.fixed_pressures == {}

    plumb.set_pressure(3, 100, True)

    assert plumb.fixed_pressures == {3: 100}
