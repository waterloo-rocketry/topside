import pytest

import topside as ops
import topside.plumbing.invalid_reasons as invalid
import topside.plumbing.exceptions as exceptions
import topside.plumbing.tests.testing_utils as test_utils
import topside.plumbing.plumbing_utils as utils

def test_add_component():
    plumb = test_utils.two_valve_setup(0.5, 0.2, 10, 'closed', 0.5, 0.2, 10, 'closed')

    pc = test_utils.create_component(0, 0, 0, 1, 'valve3', 'C')
    mapping = {
        1: 3,
        2: 4
    }

    plumb.add_component(pc, mapping, 'closed', {4: 50})

    assert plumb.valid
    assert plumb.time_resolution == int(utils.s_to_micros(0.2) / utils.DEFAULT_RESOLUTION_SCALE)
    assert list(plumb.plumbing_graph.edges(data=True, keys=True)) == [
        (1, 2, 'valve1.A1', {'FC': utils.teq_to_FC(utils.s_to_micros(10))}),
        (2, 1, 'valve1.A2', {'FC': 0}),
        (2, 3, 'valve2.B1', {'FC': utils.teq_to_FC(utils.s_to_micros(0.5))}),
        (3, 2, 'valve2.B2', {'FC': utils.teq_to_FC(utils.s_to_micros(0.2))}),
        (3, 4, 'valve3.C1', {'FC': utils.teq_to_FC(0)}),
        (4, 3, 'valve3.C2', {'FC': utils.teq_to_FC(utils.s_to_micros(1))})
    ]
    assert list(plumb.plumbing_graph.nodes(data=True)) == [
        (1, {'pressure': 0}),
        (2, {'pressure': 0}),
        (3, {'pressure': 100}),
        (4, {'pressure': 50})
    ]
    assert plumb.component_dict['valve1'].current_state == 'closed'
    assert plumb.component_dict['valve2'].current_state == 'open'
    assert plumb.component_dict['valve3'].current_state == 'closed'


def test_add_component_errors():
    plumb = test_utils.two_valve_setup(0.5, 0.2, 10, 'closed', 0.5, 0.2, 10, 'closed')

    name = 'valve3'
    wrong_node = 3
    right_node = 2
    pc = test_utils.create_component(0, 0, 0, 1, name, 'C')
    mapping = {
        1: 3,
        wrong_node: 4
    }

    with pytest.raises(exceptions.MissingInputError):
        plumb.add_component(pc, mapping, 'closed', {4: 50})
    assert not plumb.valid
    assert len(plumb.error_set) == 2

    error = invalid.InvalidComponentNode(
        f"Component '{name}', node {right_node} not found in mapping dict.",
        name, right_node)
    dup_error = invalid.DuplicateError(
        invalid.multi_error_msg(
            f"Component '{name}', node {right_node} not found in mapping dict."),
        error)

    assert error in plumb.error_set
    assert dup_error in plumb.error_set


def test_remove_component():
    plumb = test_utils.two_valve_setup(0.5, 0.2, 10, 'closed', 0.5, 0.2, 10, 'closed')
    plumb.remove_component('valve2')

    assert plumb.valid
    assert plumb.time_resolution == int(utils.s_to_micros(0.2) / utils.DEFAULT_RESOLUTION_SCALE)
    assert list(plumb.plumbing_graph.edges(data=True, keys=True)) == [
        (1, 2, 'valve1.A1', {'FC': utils.teq_to_FC(utils.s_to_micros(10))}),
        (2, 1, 'valve1.A2', {'FC': 0}),
    ]
    assert list(plumb.plumbing_graph.nodes(data=True)) == [
        (1, {'pressure': 0}),
        (2, {'pressure': 0}),
    ]
    assert plumb.component_dict['valve1'].current_state == 'closed'

def test_add_remove():
    plumb = test_utils.two_valve_setup(0.5, 0.2, 10, 'closed', 0.5, 0.2, 10, 'closed')

    pc = test_utils.create_component(0, 0, 0, 1, 'valve3', 'C')
    mapping = {
        1: 3,
        2: 4
    }

    plumb.add_component(pc, mapping, 'closed', {4: 50})

    plumb.remove_component('valve3')

    assert plumb.valid
    assert plumb.time_resolution == int(utils.s_to_micros(0.2) / utils.DEFAULT_RESOLUTION_SCALE)
    assert list(plumb.plumbing_graph.edges(data=True, keys=True)) == [
        (1, 2, 'valve1.A1', {'FC': utils.teq_to_FC(utils.s_to_micros(10))}),
        (2, 1, 'valve1.A2', {'FC': 0}),
        (2, 3, 'valve2.B1', {'FC': utils.teq_to_FC(utils.s_to_micros(0.5))}),
        (3, 2, 'valve2.B2', {'FC': utils.teq_to_FC(utils.s_to_micros(0.2))}),
    ]
    assert list(plumb.plumbing_graph.nodes(data=True)) == [
        (1, {'pressure': 0}),
        (2, {'pressure': 0}),
        (3, {'pressure': 100}),
    ]
    assert plumb.component_dict['valve1'].current_state == 'closed'
    assert plumb.component_dict['valve2'].current_state == 'open'


def test_remove_nonexistent_component():
    plumb = test_utils.two_valve_setup(0.5, 0.2, 10, 'closed', 0.5, 0.2, 10, 'closed')
    nonexistent_component = 'potato'

    with pytest.raises(exceptions.InvalidRemoveError):
        plumb.remove_component(nonexistent_component)


def test_remove_add_errors():
    plumb = test_utils.two_valve_setup(0.5, 0.2, 10, 'closed', 0.5, 0.2, 10, 'closed')

    name = 'valve3'
    wrong_node = 3
    right_node = 2
    pc = test_utils.create_component(0, 0, 0, 1, name, 'C')
    mapping = {
        1: 3,
        wrong_node: 4
    }

    with pytest.raises(exceptions.MissingInputError):
        plumb.add_component(pc, mapping, 'closed', {4: 50})
    assert not plumb.valid
    assert len(plumb.error_set) == 2
    error = invalid.InvalidComponentNode(
        f"Component '{name}', node {right_node} not found in mapping dict.",
        name, right_node)
    dup_error = invalid.DuplicateError(
        invalid.multi_error_msg(
            f"Component '{name}', node {right_node} not found in mapping dict."),
        error)
    assert error in plumb.error_set
    assert dup_error in plumb.error_set

    plumb.remove_component(name)

    assert plumb.valid
    assert plumb.time_resolution == int(utils.s_to_micros(0.2) / utils.DEFAULT_RESOLUTION_SCALE)
    assert list(plumb.plumbing_graph.edges(data=True, keys=True)) == [
        (1, 2, 'valve1.A1', {'FC': utils.teq_to_FC(utils.s_to_micros(10))}),
        (2, 1, 'valve1.A2', {'FC': 0}),
        (2, 3, 'valve2.B1', {'FC': utils.teq_to_FC(utils.s_to_micros(0.5))}),
        (3, 2, 'valve2.B2', {'FC': utils.teq_to_FC(utils.s_to_micros(0.2))}),
    ]
    assert list(plumb.plumbing_graph.nodes(data=True)) == [
        (1, {'pressure': 0}),
        (2, {'pressure': 0}),
        (3, {'pressure': 100}),
    ]
    assert plumb.component_dict['valve1'].current_state == 'closed'
    assert plumb.component_dict['valve2'].current_state == 'open'


def test_remove_errors_wrong_component_name():
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

    plumb.remove_component(wrong_component_name)

    assert plumb.valid
    assert plumb.time_resolution == int(utils.s_to_micros(0.2) / utils.DEFAULT_RESOLUTION_SCALE)
    assert list(plumb.plumbing_graph.edges(data=True, keys=True)) == [
        (2, 3, 'valve2.B1', {'FC': utils.teq_to_FC(utils.s_to_micros(0))}),
        (3, 2, 'valve2.B2', {'FC': utils.teq_to_FC(utils.s_to_micros(0))}),
    ]
    assert list(plumb.plumbing_graph.nodes(data=True)) == [
        (2, {'pressure': 0}),
        (3, {'pressure': 100}),
    ]
    assert plumb.component_dict['valve2'].current_state == 'open'
