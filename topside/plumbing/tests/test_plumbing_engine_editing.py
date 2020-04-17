import pytest

import topside as top
import topside.plumbing.invalid_reasons as invalid
import topside.plumbing.exceptions as exceptions
import topside.plumbing.tests.testing_utils as test_utils
import topside.plumbing.plumbing_utils as utils


# TODO(wendi): Add testing for specific error messages from raised errors.


def test_add_component():
    plumb = test_utils.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED_KEYWORD, 0.5, 0.2, 10, utils.CLOSED_KEYWORD)

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
    plumb = test_utils.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED_KEYWORD, 0.5, 0.2, 10, utils.CLOSED_KEYWORD)

    name = 'valve3'
    wrong_node = 3
    right_node = 2
    pc = test_utils.create_component(0, 0, 0, 1, name, 'C')
    mapping = {
        1: 3,
        wrong_node: 4
    }

    with pytest.raises(exceptions.BadInputError):
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
    plumb = test_utils.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED_KEYWORD, 0.5, 0.2, 10, utils.CLOSED_KEYWORD)
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
    old_lowest_teq = 0.2
    plumb = test_utils.two_valve_setup(
        0.5, old_lowest_teq, 10, utils.CLOSED_KEYWORD, 0.5, old_lowest_teq, 10,
        utils.CLOSED_KEYWORD)

    new_lowest_teq = 0.1
    pc = test_utils.create_component(0, 0, 0, new_lowest_teq, 'valve3', 'C')
    mapping = {
        1: 3,
        2: 4
    }

    plumb.add_component(pc, mapping, 'closed', {4: 50})

    assert plumb.time_resolution ==\
        int(utils.s_to_micros(new_lowest_teq) / utils.DEFAULT_RESOLUTION_SCALE)

    plumb.remove_component('valve3')

    assert plumb.valid
    assert plumb.time_resolution ==\
        int(utils.s_to_micros(old_lowest_teq) / utils.DEFAULT_RESOLUTION_SCALE)
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
    plumb = test_utils.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED_KEYWORD, 0.5, 0.2, 10, utils.CLOSED_KEYWORD)
    nonexistent_component = 'potato'

    with pytest.raises(exceptions.BadInputError):
        plumb.remove_component(nonexistent_component)


def test_remove_add_errors():
    plumb = test_utils.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED_KEYWORD, 0.5, 0.2, 10, utils.CLOSED_KEYWORD)

    name = 'valve3'
    wrong_node = 3
    right_node = 2
    pc = test_utils.create_component(0, 0, 0, 1, name, 'C')
    mapping = {
        1: 3,
        wrong_node: 4
    }

    with pytest.raises(exceptions.BadInputError):
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
    plumb = top.PlumbingEngine(
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


def test_reverse_orientation():
    plumb = test_utils.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED_KEYWORD, 0.5, 0.2, 10, utils.CLOSED_KEYWORD)
    plumb.reverse_orientation('valve1')

    assert plumb.valid
    assert plumb.time_resolution == int(utils.s_to_micros(0.2) / utils.DEFAULT_RESOLUTION_SCALE)
    assert list(plumb.plumbing_graph.edges(data=True, keys=True)) == [
        (1, 2, 'valve1.A1', {'FC': 0}),
        (2, 1, 'valve1.A2', {'FC': utils.teq_to_FC(utils.s_to_micros(10))}),
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


def test_reverse_orientation_wrong_component():
    wrong_name = 'potato'
    plumb = test_utils.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED_KEYWORD, 0.5, 0.2, 10, utils.CLOSED_KEYWORD)

    with pytest.raises(exceptions.BadInputError):
        plumb.reverse_orientation(wrong_name)


def test_set_pressure():
    plumb = test_utils.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED_KEYWORD, 0.5, 0.2, 10, utils.CLOSED_KEYWORD)
    pc = test_utils.create_component(0, 0, 0, 1, 'valve3', 'C')
    mapping = {
        1: 3,
        2: 4
    }
    plumb.add_component(pc, mapping, 'closed', {4: 50})

    plumb.set_pressure(1, 200)
    plumb.set_pressure(2, 7000)

    assert list(plumb.plumbing_graph.nodes(data=True)) == [
        (1, {'pressure': 200}),
        (2, {'pressure': 7000}),
        (3, {'pressure': 100}),
        (4, {'pressure': 50})
    ]

    plumb.set_pressure(4, 10)
    plumb.set_pressure(1, 0)

    assert list(plumb.plumbing_graph.nodes(data=True)) == [
        (1, {'pressure': 0}),
        (2, {'pressure': 7000}),
        (3, {'pressure': 100}),
        (4, {'pressure': 10})
    ]


def test_set_pressure_errors():
    plumb = test_utils.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED_KEYWORD, 0.5, 0.2, 10, utils.CLOSED_KEYWORD)
    pc = test_utils.create_component(0, 0, 0, 1, 'valve3', 'C')
    mapping = {
        1: 3,
        2: 4
    }
    plumb.add_component(pc, mapping, 'closed', {4: 50})

    negative_pressure = -20
    not_a_number = 'potato'
    with pytest.raises(exceptions.BadInputError):
        plumb.set_pressure(4, negative_pressure)

    with pytest.raises(exceptions.BadInputError):
        plumb.set_pressure(4, not_a_number)
    assert list(plumb.plumbing_graph.nodes(data=True)) == [
        (1, {'pressure': 0}),
        (2, {'pressure': 0}),
        (3, {'pressure': 100}),
        (4, {'pressure': 50})
    ]

    nonexistent_node = 5
    with pytest.raises(exceptions.BadInputError):
        plumb.set_pressure(nonexistent_node, 100)

    plumb.set_pressure(4, 100)
    assert list(plumb.plumbing_graph.nodes(data=True)) == [
        (1, {'pressure': 0}),
        (2, {'pressure': 0}),
        (3, {'pressure': 100}),
        (4, {'pressure': 100})
    ]


def test_set_teq():
    old_lowest_teq = 0.2
    plumb = test_utils.two_valve_setup(
        0.5, old_lowest_teq, 10, utils.CLOSED_KEYWORD, 0.5, old_lowest_teq, 10,
        utils.CLOSED_KEYWORD)

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

    assert plumb.time_resolution ==\
        int(utils.s_to_micros(new_lowest_teq) / utils.DEFAULT_RESOLUTION_SCALE)
    assert list(plumb.plumbing_graph.edges(data=True, keys=True)) == [
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
    plumb = test_utils.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED_KEYWORD, 0.5, 0.2, 10, utils.CLOSED_KEYWORD)

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

    with pytest.raises(exceptions.BadInputError):
        plumb.set_teq('valve1', bad_teq)

    with pytest.raises(exceptions.BadInputError):
        plumb.set_teq(wrong_name, which_edge)

    with pytest.raises(exceptions.BadInputError):
        plumb.set_teq('valve1', bad_key)

    with pytest.raises(exceptions.BadInputError):
        plumb.set_teq('valve1', bad_state)
