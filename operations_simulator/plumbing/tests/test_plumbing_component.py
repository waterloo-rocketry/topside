import operations_simulator as ops
import operations_simulator.plumbing.invalid_reasons as invalid
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
    assert pc1.valid
    assert not pc1.error_list


def test_minimum_teq():
    normal_teq = 1
    teq_too_low = utils.micros_to_s(utils.TEQ_MIN) / 2
    states, edges = two_edge_states_edges(normal_teq, normal_teq, normal_teq, teq_too_low)
    pc = ops.PlumbingComponent('valve', states, edges)

    assert not pc.valid
    assert len(pc.error_list) == 1
    assert isinstance(pc.error_list[0], invalid.InvalidTeq)

    error = pc.error_list[0]
    assert error.error_message ==\
        f'Provided teq value too low, minimum value is: {utils.micros_to_s(utils.TEQ_MIN)}s'
    assert error.component_name == 'valve'
    assert error.state_id == 'closed'
    assert error.edge_id == (2, 1, 'A2')
    assert error.teq == teq_too_low


def test_invalid_keyword():
    normal_teq = 1
    wrong_keyword_teq = 'potato'
    states, edges = two_edge_states_edges(normal_teq, normal_teq, normal_teq, wrong_keyword_teq)
    pc = ops.PlumbingComponent('valve', states, edges)

    assert not pc.valid
    assert len(pc.error_list) == 1
    assert isinstance(pc.error_list[0], invalid.InvalidTeq)
    assert pc.error_list[0].error_message ==\
        "Invalid provided teq value ('potato'), accepted keyword is: 'closed'"
    assert pc.error_list[0].component_name == 'valve'
    assert pc.error_list[0].state_id == 'closed'
    assert pc.error_list[0].edge_id == (2, 1, 'A2')
    assert pc.error_list[0].teq == wrong_keyword_teq


def test_multiple_errors():
    normal_teq = 1
    teq_too_low = utils.micros_to_s(utils.TEQ_MIN) / 2
    wrong_keyword_teq = 'potato'
    states, edges = two_edge_states_edges(normal_teq, normal_teq, teq_too_low, wrong_keyword_teq)
    pc = ops.PlumbingComponent('valve', states, edges)

    assert not pc.valid
    assert len(pc.error_list) == 2
    assert isinstance(pc.error_list[0], invalid.InvalidTeq) and isinstance(
        pc.error_list[1], invalid.InvalidTeq)

    error1 = pc.error_list[0]
    assert error1.error_message ==\
        f"Provided teq value too low, minimum value is: {utils.micros_to_s(utils.TEQ_MIN)}s"
    assert error1.component_name == 'valve'
    assert error1.state_id == 'closed'
    assert error1.edge_id == (1, 2, 'A1')
    assert error1.teq == teq_too_low

    error2 = pc.error_list[1]
    assert error2.error_message == \
        "Invalid provided teq value ('potato'), accepted keyword is: 'closed'"
    assert error2.component_name == 'valve'
    assert error2.state_id == 'closed'
    assert error2.edge_id == (2, 1, 'A2')
    assert error2.teq == wrong_keyword_teq


def test_component_dicts_remain_unchanged():
    teq = 5
    pc_states, edges = two_edge_states_edges(teq, teq, teq, teq)
    pc = ops.PlumbingComponent('valve', pc_states, edges)

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
