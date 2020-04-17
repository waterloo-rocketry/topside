import pytest

import topside as ops
import topside.plumbing.invalid_reasons as invalid
import topside.plumbing.exceptions as exceptions
import topside.plumbing.tests.testing_utils as test_utils
import topside.plumbing.plumbing_utils as utils


def test_empty_graph():
    plumb = ops.PlumbingEngine()

    assert plumb.time_resolution == utils.DEFAULT_TIME_RESOLUTION_MICROS
    assert not list(plumb.plumbing_graph.edges(data=True, keys=True))
    assert not list(plumb.plumbing_graph.nodes(data=True))


def test_open_closed_valves():
    plumb = test_utils.two_valve_setup(
        0, 0, utils.CLOSED_KEYWORD, utils.CLOSED_KEYWORD,
        0, 0, utils.CLOSED_KEYWORD, utils.CLOSED_KEYWORD)

    assert plumb.time_resolution == utils.DEFAULT_TIME_RESOLUTION_MICROS
    assert list(plumb.plumbing_graph.edges(data=True, keys=True)) == [
        (1, 2, 'valve1.A1', {'FC': 0}),
        (2, 1, 'valve1.A2', {'FC': 0}),
        (2, 3, 'valve2.B1', {'FC': utils.FC_MAX}),
        (3, 2, 'valve2.B2', {'FC': utils.FC_MAX})
    ]
    assert list(plumb.plumbing_graph.nodes(data=True)) == [
        (1, {'pressure': 0}),
        (2, {'pressure': 0}),
        (3, {'pressure': 100})
    ]
    assert plumb.component_dict['valve1'].current_state == 'closed'
    assert plumb.component_dict['valve2'].current_state == 'open'


def test_arbitrary_states():
    plumb = test_utils.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED_KEYWORD, 0.5, 0.2, 10, utils.CLOSED_KEYWORD)

    assert plumb.time_resolution == int(utils.s_to_micros(0.2) / utils.DEFAULT_RESOLUTION_SCALE)
    assert list(plumb.plumbing_graph.edges(data=True, keys=True)) == [
        (1, 2, 'valve1.A1', {'FC': utils.teq_to_FC(utils.s_to_micros(10))}),
        (2, 1, 'valve1.A2', {'FC': 0}),
        (2, 3, 'valve2.B1', {'FC': utils.teq_to_FC(utils.s_to_micros(0.5))}),
        (3, 2, 'valve2.B2', {'FC': utils.teq_to_FC(utils.s_to_micros(0.2))})
    ]
    assert list(plumb.plumbing_graph.nodes(data=True)) == [
        (1, {'pressure': 0}),
        (2, {'pressure': 0}),
        (3, {'pressure': 100})
    ]
    assert plumb.component_dict['valve1'].current_state == 'closed'
    assert plumb.component_dict['valve2'].current_state == 'open'


def test_load_graph_to_empty():
    plumb0 = test_utils.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED_KEYWORD, 0.5, 0.2, 10, utils.CLOSED_KEYWORD)
    pressures = {3: 100}
    default_states = {'valve1': 'closed', 'valve2': 'open'}

    plumb = ops.PlumbingEngine()
    plumb.load_graph(plumb0.component_dict, plumb0.mapping, pressures, default_states)

    assert plumb.time_resolution == int(utils.s_to_micros(0.2) / utils.DEFAULT_RESOLUTION_SCALE)
    assert list(plumb.plumbing_graph.edges(data=True, keys=True)) == [
        (1, 2, 'valve1.A1', {'FC': utils.teq_to_FC(utils.s_to_micros(10))}),
        (2, 1, 'valve1.A2', {'FC': 0}),
        (2, 3, 'valve2.B1', {'FC': utils.teq_to_FC(utils.s_to_micros(0.5))}),
        (3, 2, 'valve2.B2', {'FC': utils.teq_to_FC(utils.s_to_micros(0.2))})
    ]
    assert list(plumb.plumbing_graph.nodes(data=True)) == [
        (1, {'pressure': 0}),
        (2, {'pressure': 0}),
        (3, {'pressure': 100})
    ]
    assert plumb.component_dict['valve1'].current_state == 'closed'
    assert plumb.component_dict['valve2'].current_state == 'open'


def test_replace_graph():
    plumb0 = test_utils.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED_KEYWORD, 0.5, 0.2, 10, utils.CLOSED_KEYWORD)
    plumb = test_utils.two_valve_setup(
        0, 0, utils.CLOSED_KEYWORD, utils.CLOSED_KEYWORD, 0, 0, utils.CLOSED_KEYWORD, utils.CLOSED_KEYWORD)

    pressures = {3: 100}
    default_states = {'valve1': 'closed', 'valve2': 'open'}
    plumb.load_graph(plumb0.component_dict, plumb0.mapping, pressures, default_states)

    assert plumb.time_resolution == int(utils.s_to_micros(0.2) / utils.DEFAULT_RESOLUTION_SCALE)
    assert list(plumb.plumbing_graph.edges(data=True, keys=True)) == [
        (1, 2, 'valve1.A1', {'FC': utils.teq_to_FC(utils.s_to_micros(10))}),
        (2, 1, 'valve1.A2', {'FC': 0}),
        (2, 3, 'valve2.B1', {'FC': utils.teq_to_FC(utils.s_to_micros(0.5))}),
        (3, 2, 'valve2.B2', {'FC': utils.teq_to_FC(utils.s_to_micros(0.2))})
    ]
    assert list(plumb.plumbing_graph.nodes(data=True)) == [
        (1, {'pressure': 0}),
        (2, {'pressure': 0}),
        (3, {'pressure': 100})
    ]
    assert plumb.component_dict['valve1'].current_state == 'closed'
    assert plumb.component_dict['valve2'].current_state == 'open'


def test_new_component_state():
    plumb = test_utils.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED_KEYWORD, 0.5, 0.2, 10, utils.CLOSED_KEYWORD)
    plumb.set_component_state('valve1', 'open')

    assert list(plumb.plumbing_graph.edges(data=True, keys=True)) == [
        (1, 2, 'valve1.A1', {'FC': utils.teq_to_FC(utils.s_to_micros(0.5))}),
        (2, 1, 'valve1.A2', {'FC': utils.teq_to_FC(utils.s_to_micros(0.2))}),
        (2, 3, 'valve2.B1', {'FC': utils.teq_to_FC(utils.s_to_micros(0.5))}),
        (3, 2, 'valve2.B2', {'FC': utils.teq_to_FC(utils.s_to_micros(0.2))})
    ]
    assert plumb.component_dict['valve1'].current_state == 'open'
    assert plumb.component_dict['valve2'].current_state == 'open'


def test_missing_component():
    wrong_component_name = 'potato'
    pc1 = test_utils.create_component(0, 0, 0, 0, 'valve1', 'A')
    pc2 = test_utils.create_component(0, 0, 0, 0, 'valve2', 'B')

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
    plumb = ops.PlumbingEngine(
        {wrong_component_name: pc1, 'valve2': pc2}, component_mapping, pressures, default_states)

    assert not plumb.valid
    assert len(plumb.error_set) == 2

    error1 = invalid.InvalidComponentName(
        f"Component with name '{wrong_component_name}' not found in provided mapping dict.",
        wrong_component_name)

    error2 = invalid.InvalidComponentName(
        f"Component '{wrong_component_name}' state not found in initial states dict.",
        wrong_component_name)

    assert error1 in plumb.error_set
    assert error2 in plumb.error_set


def test_wrong_node_mapping():
    # The node name should be 1.
    proper_node_name = 1
    wrong_node_name = 5
    pc1 = test_utils.create_component(0, 0, 0, 0, 'valve1', 'A')
    pc2 = test_utils.create_component(0, 0, 0, 0, 'valve2', 'B')

    component_mapping = {
        'valve1': {
            wrong_node_name: 1,
            2: 2
        },
        'valve2': {
            1: 2,
            2: 3
        }
    }

    pressures = {3: 100}
    default_states = {'valve1': 'closed', 'valve2': 'open'}
    plumb = ops.PlumbingEngine(
        {'valve1': pc1, 'valve2': pc2}, component_mapping, pressures, default_states)

    assert not plumb.valid

    # Since the node name is wrong in the mapping, an error should be added
    # every time the mapping dict is accessed to find the matching graph node.
    # This translates to twice (once per component) when populating the main graph,
    # and twice (once per component) when assigning initial states by component,
    # since the component node stored in the component's states dict needs to be
    # translated into a main graph node. So 4 errors total, but they're identical
    # so we should get one original error and one multi-error note.
    assert len(plumb.error_set) == 2

    error = invalid.InvalidComponentNode(
        f"Component 'valve1', node {proper_node_name} not found in mapping dict.",
        'valve1', proper_node_name)

    duplicate_error = invalid.DuplicateError(invalid.multi_error_msg(
        f"Component 'valve1', node {proper_node_name} not found in mapping dict."), error)

    assert error in plumb.error_set
    assert duplicate_error in plumb.error_set


def test_missing_node_pressure():
    wrong_node_name = 4
    pc1 = test_utils.create_component(0, 0, 0, 0, 'valve1', 'A')
    pc2 = test_utils.create_component(0, 0, 0, 0, 'valve2', 'B')

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

    pressures = {wrong_node_name: 100}
    default_states = {'valve1': 'closed', 'valve2': 'open'}
    plumb = ops.PlumbingEngine(
        {'valve1': pc1, 'valve2': pc2}, component_mapping, pressures, default_states)

    assert not plumb.valid
    assert len(plumb.error_set) == 1

    error = invalid.InvalidNodePressure(
        f"Node {wrong_node_name} not found in initial node pressures dict.", wrong_node_name)

    assert error in plumb.error_set


def test_missing_initial_state():
    wrong_component_name = 'potato'
    proper_component_name = 'valve1'
    pc1 = test_utils.create_component(0, 0, 0, 0, 'valve1', 'A')
    pc2 = test_utils.create_component(0, 0, 0, 0, 'valve2', 'B')

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
    plumb = ops.PlumbingEngine(
        {'valve1': pc1, 'valve2': pc2}, component_mapping, pressures, default_states)

    assert not plumb.valid
    assert len(plumb.error_set) == 1

    error = invalid.InvalidComponentName(
        f"Component '{proper_component_name}' state not found in initial states dict.",
        proper_component_name)

    assert error in plumb.error_set


def test_error_reset():
    wrong_component_name = 'potato'
    pc1 = test_utils.create_component(0, 0, 0, 0, 'valve1', 'A')
    pc2 = test_utils.create_component(0, 0, 0, 0, 'valve2', 'B')

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
    plumb = ops.PlumbingEngine(
        {wrong_component_name: pc1, 'valve2': pc2}, component_mapping, pressures, default_states)

    assert not plumb.valid

    plumb = ops.PlumbingEngine()

    assert plumb.valid


def test_set_component_wrong_state_name():
    wrong_state_name = 'potato'
    plumb = test_utils.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED_KEYWORD, 0.5, 0.2, 10, utils.CLOSED_KEYWORD)
    with pytest.raises(exceptions.BadInputError):
        plumb.set_component_state('valve1', wrong_state_name)


def test_set_component_wrong_component_name():
    wrong_component_name = 'potato'
    plumb = test_utils.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED_KEYWORD, 0.5, 0.2, 10, utils.CLOSED_KEYWORD)
    with pytest.raises(exceptions.BadInputError):
        plumb.set_component_state(wrong_component_name, 'open')


def test_plumbing_engines_independent():
    plumb1 = ops.PlumbingEngine()
    plumb2 = ops.PlumbingEngine()

    key = 'f'
    value = 1
    plumb1.mapping[key] = value

    plumb3 = ops.PlumbingEngine()

    assert plumb1.mapping == {key: value}
    assert plumb2.mapping == {}
    assert plumb3.mapping == {}


def test_engine_dicts_remain_unchanged():
    pc1 = test_utils.create_component(0, 0, 0, 0, 'valve1', 'A')
    pc2 = test_utils.create_component(0, 0, 0, 0, 'valve2', 'B')

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
    plumb = ops.PlumbingEngine(
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
    pc1 = test_utils.create_component(0, 0, 0, 0, 'valve1', 'A')
    pc2 = test_utils.create_component(0, 0, 0, 0, 'valve2', 'B')

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
    plumb = ops.PlumbingEngine(
        {wrong_component_name: pc1, 'valve2': pc2}, component_mapping, pressures, default_states)

    assert not plumb.valid
    assert len(plumb.error_set) == 2

    error1 = invalid.InvalidComponentName(
        f"Component with name '{wrong_component_name}' not found in provided mapping dict.",
        wrong_component_name)

    error2 = invalid.InvalidComponentName(
        f"Component '{wrong_component_name}' state not found in initial states dict.",
        wrong_component_name)

    assert error1 in plumb.error_set
    assert error2 in plumb.error_set

    plumb0 = test_utils.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED_KEYWORD, 0.5, 0.2, 10, utils.CLOSED_KEYWORD)
    pressures = {3: 100}
    default_states = {'valve1': 'closed', 'valve2': 'open'}

    plumb.load_graph(plumb0.component_dict, plumb0.mapping, pressures, default_states)

    assert plumb.valid
    assert len(plumb.error_set) == 0
