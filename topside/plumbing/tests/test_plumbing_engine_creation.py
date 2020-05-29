import pytest

import topside as top
import topside.plumbing.invalid_reasons as invalid
import topside.plumbing.exceptions as exceptions
import topside.plumbing.tests.testing_utils as test
import topside.plumbing.plumbing_utils as utils


def test_empty_graph():
    plumb = top.PlumbingEngine()

    assert plumb.time_res == utils.DEFAULT_TIME_RESOLUTION_MICROS
    assert not plumb.edges()
    assert not plumb.nodes()


def test_open_closed_valves():
    plumb = test.two_valve_setup(
        0, 0, utils.CLOSED, utils.CLOSED,
        0, 0, utils.CLOSED, utils.CLOSED)

    assert plumb.time_res == utils.DEFAULT_TIME_RESOLUTION_MICROS
    assert plumb.edges() == [
        (1, 2, 'valve1.A1', {'FC': 0}),
        (2, 1, 'valve1.A2', {'FC': 0}),
        (2, 3, 'valve2.B1', {'FC': utils.FC_MAX}),
        (3, 2, 'valve2.B2', {'FC': utils.FC_MAX})
    ]
    assert plumb.nodes() == [
        (1, {'pressure': 0}),
        (2, {'pressure': 0}),
        (3, {'pressure': 100})
    ]
    assert plumb.current_state('valve1') == 'closed'
    assert plumb.current_state('valve2') == 'open'


def test_arbitrary_states():
    plumb = test.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED, 0.5, 0.2, 10, utils.CLOSED)

    assert plumb.time_res == int(utils.s_to_micros(0.2) / utils.DEFAULT_RESOLUTION_SCALE)
    assert plumb.edges() == [
        (1, 2, 'valve1.A1', {'FC': utils.teq_to_FC(utils.s_to_micros(10))}),
        (2, 1, 'valve1.A2', {'FC': 0}),
        (2, 3, 'valve2.B1', {'FC': utils.teq_to_FC(utils.s_to_micros(0.5))}),
        (3, 2, 'valve2.B2', {'FC': utils.teq_to_FC(utils.s_to_micros(0.2))})
    ]
    assert plumb.nodes() == [
        (1, {'pressure': 0}),
        (2, {'pressure': 0}),
        (3, {'pressure': 100})
    ]
    assert plumb.current_state('valve1') == 'closed'
    assert plumb.current_state('valve2') == 'open'


def test_load_graph_to_empty():
    plumb0 = test.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED, 0.5, 0.2, 10, utils.CLOSED)
    pressures = {3: 100}
    default_states = {'valve1': 'closed', 'valve2': 'open'}

    plumb = top.PlumbingEngine()
    plumb.load_graph(plumb0.component_dict, plumb0.mapping, pressures, default_states)

    assert plumb.time_res == int(utils.s_to_micros(0.2) / utils.DEFAULT_RESOLUTION_SCALE)
    assert plumb.edges() == [
        (1, 2, 'valve1.A1', {'FC': utils.teq_to_FC(utils.s_to_micros(10))}),
        (2, 1, 'valve1.A2', {'FC': 0}),
        (2, 3, 'valve2.B1', {'FC': utils.teq_to_FC(utils.s_to_micros(0.5))}),
        (3, 2, 'valve2.B2', {'FC': utils.teq_to_FC(utils.s_to_micros(0.2))})
    ]
    assert plumb.nodes() == [
        (1, {'pressure': 0}),
        (2, {'pressure': 0}),
        (3, {'pressure': 100})
    ]
    assert plumb.current_state('valve1') == 'closed'
    assert plumb.current_state('valve2') == 'open'


def test_replace_graph():
    plumb0 = test.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED, 0.5, 0.2, 10, utils.CLOSED)
    plumb = test.two_valve_setup(
        0, 0, utils.CLOSED, utils.CLOSED,
        0, 0, utils.CLOSED, utils.CLOSED)

    pressures = {3: 100}
    default_states = {'valve1': 'closed', 'valve2': 'open'}
    plumb.load_graph(plumb0.component_dict, plumb0.mapping, pressures, default_states)

    assert plumb.time_res == int(utils.s_to_micros(0.2) / utils.DEFAULT_RESOLUTION_SCALE)
    assert plumb.edges() == [
        (1, 2, 'valve1.A1', {'FC': utils.teq_to_FC(utils.s_to_micros(10))}),
        (2, 1, 'valve1.A2', {'FC': 0}),
        (2, 3, 'valve2.B1', {'FC': utils.teq_to_FC(utils.s_to_micros(0.5))}),
        (3, 2, 'valve2.B2', {'FC': utils.teq_to_FC(utils.s_to_micros(0.2))})
    ]
    assert plumb.nodes() == [
        (1, {'pressure': 0}),
        (2, {'pressure': 0}),
        (3, {'pressure': 100})
    ]
    assert plumb.current_state('valve1') == 'closed'
    assert plumb.current_state('valve2') == 'open'


def test_new_component_state():
    plumb = test.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED, 0.5, 0.2, 10, utils.CLOSED)
    plumb.set_component_state('valve1', 'open')

    assert plumb.edges() == [
        (1, 2, 'valve1.A1', {'FC': utils.teq_to_FC(utils.s_to_micros(0.5))}),
        (2, 1, 'valve1.A2', {'FC': utils.teq_to_FC(utils.s_to_micros(0.2))}),
        (2, 3, 'valve2.B1', {'FC': utils.teq_to_FC(utils.s_to_micros(0.5))}),
        (3, 2, 'valve2.B2', {'FC': utils.teq_to_FC(utils.s_to_micros(0.2))})
    ]
    assert plumb.current_state('valve1') == 'open'
    assert plumb.current_state('valve2') == 'open'


def test_invalid_component():
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

    plumb = top.PlumbingEngine()

    with pytest.raises(exceptions.BadInputError) as err:
        plumb.load_graph({'valve': invalid_pc}, {1: 1, 2: 2}, {1: 100}, {'valve': 'open'})
    assert str(err.value) == "Node 1 not found in graph."

    assert not plumb.is_valid()
    assert len(plumb.errors()) == 1

    error = invalid.InvalidComponentName(
        "Component with name 'valve' is not valid;"
        " component cannot be loaded in until errors are resolved.", 'valve')
    assert error in plumb.errors()


def test_missing_component():
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
    assert len(plumb.errors()) == 2

    error1 = invalid.InvalidComponentName(
        f"Component with name '{wrong_component_name}' not found in mapping dict.",
        wrong_component_name)

    error2 = invalid.InvalidComponentName(
        f"Component '{wrong_component_name}' state not found in initial states dict.",
        wrong_component_name)

    assert error1 in plumb.errors()
    assert error2 in plumb.errors()


def test_wrong_node_mapping():
    proper_node_name = 1
    wrong_node_name = 5
    pc1 = test.create_component(0, 0, 0, 0, 'valve1', 'A')
    pc2 = test.create_component(0, 0, 0, 0, 'valve2', 'B')

    component_mapping = {
        'valve1': {
            wrong_node_name: 1,
            2: 8
        },
        'valve2': {
            1: 8,
            2: 3
        }
    }

    pressures = {3: 100}
    default_states = {'valve1': 'closed', 'valve2': 'open'}
    plumb = top.PlumbingEngine(
        {'valve1': pc1, 'valve2': pc2}, component_mapping, pressures, default_states)

    assert not plumb.is_valid()

    # Since the node name is wrong in the mapping, an error should be added
    # every time the mapping dict is accessed to find the matching graph node.
    # This translates to twice (once per component) when populating the main graph,
    # and twice (once per component) when assigning initial states by component,
    # since the component node stored in the component's states dict needs to be
    # translated into a main graph node. So 4 errors total, but they're identical
    # so we should get one original error and one multi-error note.
    assert len(plumb.errors()) == 2

    error = invalid.InvalidComponentNode(
        f"Component 'valve1', node {proper_node_name} not found in mapping dict.",
        'valve1', proper_node_name)

    duplicate_error = invalid.DuplicateError(invalid.multi_error_msg(
        f"Component 'valve1', node {proper_node_name} not found in mapping dict."), error)

    assert error in plumb.errors()
    assert duplicate_error in plumb.errors()


def test_missing_node_pressure():
    wrong_node_name = 4
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

    pressures = {wrong_node_name: 100, 2: 100}
    default_states = {'valve1': 'closed', 'valve2': 'open'}
    with pytest.raises(exceptions.BadInputError) as err:
        plumb = top.PlumbingEngine(
            {'valve1': pc1, 'valve2': pc2}, component_mapping, pressures, default_states)
    assert str(err.value) == f"Node {wrong_node_name} not found in graph."


def test_missing_initial_state():
    wrong_component_name = 'potato'
    proper_component_name = 'valve1'
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
    default_states = {wrong_component_name: 'closed', 'valve2': 'open'}
    plumb = top.PlumbingEngine(
        {'valve1': pc1, 'valve2': pc2}, component_mapping, pressures, default_states)

    assert not plumb.is_valid()
    assert len(plumb.errors()) == 1

    error = invalid.InvalidComponentName(
        f"Component '{proper_component_name}' state not found in initial states dict.",
        proper_component_name)

    assert error in plumb.errors()


def test_error_reset():
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

    plumb = top.PlumbingEngine()

    assert plumb.is_valid()


def test_set_component_wrong_state_name():
    wrong_state_name = 'potato'
    plumb = test.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED, 0.5, 0.2, 10, utils.CLOSED)
    with pytest.raises(exceptions.BadInputError) as err:
        plumb.set_component_state('valve1', wrong_state_name)
    assert str(err.value) == f"State '{wrong_state_name}' not found in valve1 states dict."


def test_set_component_wrong_component_name():
    wrong_component_name = 'potato'
    plumb = test.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED, 0.5, 0.2, 10, utils.CLOSED)
    with pytest.raises(exceptions.BadInputError) as err:
        plumb.set_component_state(wrong_component_name, 'open')
    assert str(err.value) == f"Component '{wrong_component_name}' not found in mapping dict."


def test_plumbing_engines_independent():
    plumb1 = top.PlumbingEngine()
    plumb2 = top.PlumbingEngine()

    key = 'f'
    value = 1
    plumb1.mapping[key] = value

    plumb3 = top.PlumbingEngine()

    assert plumb1.mapping == {key: value}
    assert plumb2.mapping == {}
    assert plumb3.mapping == {}


def test_engine_dicts_remain_unchanged():
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
    component_dict = {'valve1': pc1, 'valve2': pc2}
    plumb = top.PlumbingEngine(
        component_dict, component_mapping, pressures, default_states)

    assert component_mapping == {
        'valve1': {
            1: 1,
            2: 2
        },
        'valve2': {
            1: 2,
            2: 3
        }
    }
    assert pressures == {3: 100}
    assert default_states == {'valve1': 'closed', 'valve2': 'open'}
    assert component_dict == {'valve1': pc1, 'valve2': pc2}


def test_load_errorless_graph():
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
    assert len(plumb.errors()) == 2

    error1 = invalid.InvalidComponentName(
        f"Component with name '{wrong_component_name}' not found in mapping dict.",
        wrong_component_name)

    error2 = invalid.InvalidComponentName(
        f"Component '{wrong_component_name}' state not found in initial states dict.",
        wrong_component_name)

    assert error1 in plumb.errors()
    assert error2 in plumb.errors()

    plumb0 = test.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED, 0.5, 0.2, 10, utils.CLOSED)
    pressures = {3: 100}
    default_states = {'valve1': 'closed', 'valve2': 'open'}

    plumb.load_graph(plumb0.component_dict, plumb0.mapping, pressures, default_states)

    assert plumb.is_valid()
