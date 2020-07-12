import copy
import pytest

import topside as top
import topside.plumbing.invalid_reasons as invalid
import topside.plumbing.exceptions as exceptions
import topside.plumbing.tests.testing_utils as test
import topside.plumbing.plumbing_utils as utils


def test_current_state():
    plumb = test.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED, 0.5, 0.2, 10, utils.CLOSED)
    wrong_name = 'potato'

    assert plumb.current_state('valve1') == 'closed'
    assert plumb.current_state('valve2') == 'open'

    plumb.set_component_state('valve1', 'open')

    assert plumb.current_state('valve1') == 'open'
    assert plumb.current_state(['valve1']) == 'open'

    assert plumb.current_state() == {
        'valve1': 'open',
        'valve2': 'open'
    }

    assert plumb.current_state('valve1', 'valve2') == {
        'valve1': 'open',
        'valve2': 'open'
    }

    list_valves = ['valve1', 'valve2']
    assert plumb.current_state(list_valves) == {
        'valve1': 'open',
        'valve2': 'open'
    }

    tuple_valves = ('valve1', 'valve2')
    assert plumb.current_state(tuple_valves) == {
        'valve1': 'open',
        'valve2': 'open'
    }

    assert plumb.current_state(['valve1'], 'valve2') == {
        'valve1': 'open',
        'valve2': 'open'
    }

    with pytest.raises(exceptions.BadInputError) as err:
        plumb.current_state(wrong_name)
    assert str(err.value) == f"Component '{wrong_name}' not found in component dict."

    with pytest.raises(exceptions.BadInputError) as err:
        plumb.current_state('valve1', wrong_name, 'valve2')
    assert str(err.value) == f"Component '{wrong_name}' not found in component dict."


def test_current_pressures():
    plumb = test.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED, 0.5, 0.2, 10, utils.CLOSED)

    plumb.set_pressure(2, 50)
    plumb.set_pressure(1, 100)

    assert plumb.current_pressures() == {
        1: 100,
        2: 50,
        3: 100
    }

    assert plumb.current_pressures(1, 2) == {
        1: 100,
        2: 50
    }

    nodes = [1, 2]
    assert plumb.current_pressures(nodes) == {
        1: 100,
        2: 50
    }

    tuple_nodes = (1, 2)
    assert plumb.current_pressures(tuple_nodes) == {
        1: 100,
        2: 50
    }

    # I don't know why you'd ever do this but if you want to you can
    assert plumb.current_pressures([1], 2) == {
        1: 100,
        2: 50
    }

    assert plumb.current_pressures(3) == 100

    wrong_node = 4
    with pytest.raises(exceptions.BadInputError) as err:
        plumb.current_pressures(wrong_node)
    assert str(err.value) == f"Node {wrong_node} not found in graph."


def test_current_FC():
    plumb = test.two_valve_setup(
        0.5, 0.2, 10, utils.CLOSED, 0.5, 0.2, 10, utils.CLOSED)

    assert plumb.current_FC() == {
        (1, 2, 'valve1.A1'): utils.teq_to_FC(utils.s_to_micros(10)),
        (2, 1, 'valve1.A2'): 0,
        (2, 3, 'valve2.B1'): utils.teq_to_FC(utils.s_to_micros(0.5)),
        (3, 2, 'valve2.B2'): utils.teq_to_FC(utils.s_to_micros(0.2))
    }

    list_valves = ['valve1', 'valve2']
    assert plumb.current_FC(list_valves) == {
        (1, 2, 'valve1.A1'): utils.teq_to_FC(utils.s_to_micros(10)),
        (2, 1, 'valve1.A2'): 0,
        (2, 3, 'valve2.B1'): utils.teq_to_FC(utils.s_to_micros(0.5)),
        (3, 2, 'valve2.B2'): utils.teq_to_FC(utils.s_to_micros(0.2))
    }

    assert plumb.current_FC((1, 2, 'valve1.A1')) == utils.teq_to_FC(utils.s_to_micros(10))

    assert plumb.current_FC((1, 2, 'valve1.A1'), (2, 3, 'valve2.B1')) == {
        (1, 2, 'valve1.A1'): utils.teq_to_FC(utils.s_to_micros(10)),
        (2, 3, 'valve2.B1'): utils.teq_to_FC(utils.s_to_micros(0.5))
    }

    assert plumb.current_FC('valve1') == {
        (1, 2, 'valve1.A1'): utils.teq_to_FC(utils.s_to_micros(10)),
        (2, 1, 'valve1.A2'): 0,
    }

    wrong_name = 'potato'
    with pytest.raises(exceptions.BadInputError) as err:
        plumb.current_FC(wrong_name)
    assert str(err.value) == f"'{wrong_name}' not found as component name or edge identifier."

    with pytest.raises(exceptions.BadInputError) as err:
        plumb.current_FC((1, 2, wrong_name))
    assert str(err.value) ==\
        f"'(1, 2, '{wrong_name}')' not found as component name or edge identifier."


def test_FC_name_overlap():
    pc1 = test.create_component(0, 0, 0, 0, 'fill_valve', 'A')
    pc2 = test.create_component(1, 1, 1, 1, 'remote_fill_valve', 'B')

    component_mapping = {
        'fill_valve': {
            1: 1,
            2: 2
        },
        'remote_fill_valve': {
            1: 2,
            2: 3
        }
    }

    pressures = {3: (100, False)}
    default_states = {'fill_valve': 'closed', 'remote_fill_valve': 'open'}
    plumb = top.PlumbingEngine(
        {'fill_valve': pc1, 'remote_fill_valve': pc2}, component_mapping, pressures, default_states)

    assert plumb.current_FC('fill_valve') == {
        (1, 2, 'fill_valve.A1'): utils.FC_MAX,
        (2, 1, 'fill_valve.A2'): utils.FC_MAX
    }

    # Since these edges belongs only to remote_fill_valve
    assert (2, 3, 'remote_fill_valve.B1') not in plumb.current_FC('fill_valve')
    assert (3, 2, 'remote_fill_valve.B2') not in plumb.current_FC('fill_valve')

    assert plumb.current_FC('remote_fill_valve') == {
        (2, 3, 'remote_fill_valve.B1'): utils.teq_to_FC(utils.s_to_micros(1)),
        (3, 2, 'remote_fill_valve.B2'): utils.teq_to_FC(utils.s_to_micros(1))
    }


def test_list_functions():
    pc1 = test.create_component(0.5, 0.2, 10, utils.CLOSED, 'valve1', 'A')
    pc2 = test.create_component(0.5, 0.2, 10, utils.CLOSED, 'valve2', 'B')

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

    negative_pressure = -50
    pressures = {3: (negative_pressure, False)}
    default_states = {'valve1': 'closed', 'valve2': 'open'}
    plumb = top.PlumbingEngine(
        {'valve1': pc1, 'valve2': pc2}, component_mapping, pressures, default_states)

    assert plumb.edges() == [
        (1, 2, 'valve1.A1', {'FC': utils.teq_to_FC(utils.s_to_micros(10))}),
        (2, 1, 'valve1.A2', {'FC': 0}),
        (2, 3, 'valve2.B1', {'FC': utils.teq_to_FC(utils.s_to_micros(0.5))}),
        (3, 2, 'valve2.B2', {'FC': utils.teq_to_FC(utils.s_to_micros(0.2))})
    ]

    assert plumb.edges(data=False) == [
        (1, 2, 'valve1.A1'),
        (2, 1, 'valve1.A2'),
        (2, 3, 'valve2.B1'),
        (3, 2, 'valve2.B2')
    ]

    # Pressure at node 3 will be 0, since the provided one was invalid
    assert plumb.nodes() == [
        (1, {'pressure': 0}),
        (2, {'pressure': 0}),
        (3, {'pressure': 0})
    ]

    assert plumb.nodes(data=False) == [1, 2, 3]

    assert plumb.errors() == {
        invalid.InvalidNodePressure(f"Negative pressure {negative_pressure} not allowed.", 3)
    }


def test_components():
    plumb = test.two_valve_setup(1, 1, 1, 1, 1, 1, 1, 1)
    original_components = copy.deepcopy(plumb.component_dict)
    queried_components = plumb.components()

    assert list(original_components.keys()) == list(queried_components.keys())

    queried_components.pop('valve1')

    # make sure that changes to the returned dict aren't propagated through to the original
    assert list(original_components.keys()) == list(plumb.component_dict.keys())
    assert list(original_components.keys()) == list(plumb.components().keys())
