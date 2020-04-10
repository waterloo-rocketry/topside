import pytest

import operations_simulator as ops
import operations_simulator.plumbing.plumbing_utils as utils


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
    pc1_states, pc1_edges = two_edge_states_edges(0, 0, 'closed', 'closed')
    pc1 = ops.PlumbingComponent('valve1', pc1_states, pc1_edges)

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


def test_minimum_teq():
    normal_teq = 1
    teq_too_low = utils.micros_to_s(utils.TEQ_MIN) / 2
    states, edges = two_edge_states_edges(normal_teq, normal_teq, normal_teq, teq_too_low)
    with pytest.raises(ValueError):
        pc = ops.PlumbingComponent('valve', states, edges)
