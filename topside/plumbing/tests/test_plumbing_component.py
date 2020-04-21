import topside as top
import topside.plumbing.invalid_reasons as invalid
import topside.plumbing.plumbing_utils as utils


def two_edge_states_edges(s1e1, s1e2, s2e1, s2e2):
    states = {
        'open': {
            (1, 2, 'A1'): s1e1,
            (2, 1, 'A2'): s1e2
        },
        'closed': {
            (1, 2, 'A1'): s2e1,
            (2, 1, 'A2'): s2e2
        }
    }
    edges = [(1, 2, 'A1'), (2, 1, 'A2')]

    return (states, edges)


def test_plumbing_component_setup():
    pc1_states, pc1_edges = two_edge_states_edges(
        0, 0, utils.CLOSED_KEYWORD, utils.CLOSED_KEYWORD)
    pc1 = top.PlumbingComponent('valve1', pc1_states, pc1_edges)

    assert pc1.current_state is None
    assert list(pc1.component_graph.edges(keys=True)) == [
        (1, 2, 'A1'),
        (2, 1, 'A2')
    ]
    assert list(pc1.component_graph.nodes()) == [1, 2]
    assert pc1.states == {
        'open': {
            (1, 2, 'A1'): utils.FC_MAX,
            (2, 1, 'A2'): utils.FC_MAX
        },
        'closed': {
            (1, 2, 'A1'): 0,
            (2, 1, 'A2'): 0
        }
    }
    assert pc1.is_valid()
    assert not pc1.error_set


def test_minimum_teq():
    normal_teq = 1
    teq_too_low = utils.micros_to_s(utils.TEQ_MIN) / 2
    states, edges = two_edge_states_edges(normal_teq, normal_teq, normal_teq, teq_too_low)
    pc = top.PlumbingComponent('valve', states, edges)

    assert not pc.is_valid()
    assert len(pc.error_set) == 1

    error = invalid.InvalidTeq(
        f'Provided teq value too low, minimum value is: {utils.micros_to_s(utils.TEQ_MIN)}s',
        'valve', 'closed', (2, 1, 'A2'), teq_too_low)
    assert error in pc.error_set


def test_invalid_keyword():
    normal_teq = 1
    wrong_keyword_teq = 'potato'
    states, edges = two_edge_states_edges(normal_teq, normal_teq, normal_teq, wrong_keyword_teq)
    pc = top.PlumbingComponent('valve', states, edges)

    assert not pc.is_valid()
    assert len(pc.error_set) == 1

    error = invalid.InvalidTeq(
        f"Invalid provided teq value ('potato'), accepted keyword is: '{utils.CLOSED_KEYWORD}'",
        'valve', 'closed', (2, 1, 'A2'), wrong_keyword_teq)

    assert error in pc.error_set


def test_edge_id_error():
    wrong_node = 5

    states = {
        'open': {
            (wrong_node, 2, 'A1'): 0,
            (2, 1, 'A2'): 0
        },
        'closed': {
            (1, 2, 'A1'): 0,
            (2, 1, 'A2'): 0
        }
    }
    edges = [(1, 2, 'A1'), (2, 1, 'A2')]

    pc = top.PlumbingComponent('valve', states, edges)

    assert not pc.is_valid()
    error = invalid.InvalidComponentEdge(
        f"Edge '({wrong_node}, 2, 'A1')' not found in provided edge list.", (wrong_node, 2, 'A1'))
    assert error in pc.error_set


def test_multiple_errors():
    normal_teq = 1
    teq_too_low = utils.micros_to_s(utils.TEQ_MIN) / 2
    wrong_keyword_teq = 'potato'
    states, edges = two_edge_states_edges(normal_teq, normal_teq, teq_too_low, wrong_keyword_teq)
    pc = top.PlumbingComponent('valve', states, edges)

    assert not pc.is_valid()
    assert len(pc.error_set) == 2

    error1 = invalid.InvalidTeq(
        f"Provided teq value too low, minimum value is: {utils.micros_to_s(utils.TEQ_MIN)}s",
        'valve', 'closed', (1, 2, 'A1'), teq_too_low)

    error2 = invalid.InvalidTeq(
        f"Invalid provided teq value ('{wrong_keyword_teq}'),"
        f" accepted keyword is: '{utils.CLOSED_KEYWORD}'",
        'valve', 'closed', (2, 1, 'A2'), wrong_keyword_teq)

    assert error1 in pc.error_set
    assert error2 in pc.error_set


def test_component_dicts_remain_unchanged():
    teq = 5
    pc_states, edges = two_edge_states_edges(teq, teq, teq, teq)
    pc = top.PlumbingComponent('valve', pc_states, edges)

    assert pc_states == two_edge_states_edges(teq, teq, teq, teq)[0]
    assert pc_states != {
        'open': {
            (1, 2, 'A1'): utils.teq_to_FC(teq),
            (2, 1, 'A2'): utils.teq_to_FC(teq)
        },
        'closed': {
            (1, 2, 'B1'): utils.teq_to_FC(teq),
            (2, 1, 'B2'): utils.teq_to_FC(teq)
        }
    }
