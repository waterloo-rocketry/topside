import pytest

import topside as top


class NeverSatisfied:
    def update(self, state):
        pass

    def satisfied(self):
        return False


def one_component_engine():
    states = {
        'open': {
            (1, 2, 'A1'): 1,
            (2, 1, 'A2'): 1
        },
        'closed': {
            (1, 2, 'A1'): top.CLOSED,
            (2, 1, 'A2'): top.CLOSED
        },
        'halfway_open': {
            (1, 2, 'A1'): 100,
            (2, 1, 'A2'): 100
        }
    }
    edges = [(1, 2, 'A1'), (2, 1, 'A2')]

    c1 = top.PlumbingComponent('c1', states, edges)

    mapping = {'c1': {1: 1, 2: 2}}
    pressures = {1: (0, False), 2: (0, False)}
    initial_states = {'c1': 'closed'}

    return top.PlumbingEngine({'c1': c1}, mapping, pressures, initial_states)


def linear_procedure():
    open_action = top.Action('c1', 'open')
    close_action = top.Action('c1', 'closed')

    s1 = top.ProcedureStep('s1', None, {top.Immediate(): 's2'})
    s2 = top.ProcedureStep('s2', open_action, {top.Immediate(): 's3'})
    s3 = top.ProcedureStep('s3', close_action, {})

    return {'s1': s1, 's2': s2, 's3': s3}


def branching_procedure_no_options():
    open_action = top.Action('c1', 'open')
    halfway_open_action = top.Action('c1', 'halfway_open')

    s1 = top.ProcedureStep('s1', None, {NeverSatisfied(): 's2',
                                        NeverSatisfied(): 's3'})
    s2 = top.ProcedureStep('s2', halfway_open_action, {})
    s3 = top.ProcedureStep('s3', open_action, {})

    return {'s1': s1, 's2': s2, 's3': s3}


def branching_procedure_one_option():
    open_action = top.Action('c1', 'open')
    halfway_open_action = top.Action('c1', 'halfway_open')

    s1 = top.ProcedureStep('s1', None, {NeverSatisfied(): 's2',
                                        top.Immediate(): 's3'})
    s2 = top.ProcedureStep('s2', halfway_open_action, {})
    s3 = top.ProcedureStep('s3', open_action, {})

    return {'s1': s1, 's2': s2, 's3': s3}


def branching_procedure_two_options():
    open_action = top.Action('c1', 'open')
    halfway_open_action = top.Action('c1', 'halfway_open')

    s1 = top.ProcedureStep('s1', None, {top.Immediate(): 's2',
                                        top.Immediate(): 's3'})
    s2 = top.ProcedureStep('s2', halfway_open_action, {})
    s3 = top.ProcedureStep('s3', open_action, {})

    return {'s1': s1, 's2': s2, 's3': s3}


def test_execute_custom_action():
    plumb_eng = one_component_engine()
    proc_eng = top.ProceduresEngine(plumb_eng)

    action = top.Action('c1', 'open')

    assert plumb_eng.current_state('c1') == 'closed'
    proc_eng.execute(action)
    assert plumb_eng.current_state('c1') == 'open'


def test_ready_to_advance_if_condition_satisfied():
    proc_eng = top.ProceduresEngine(None, linear_procedure(), 's1')

    assert proc_eng.ready_to_advance() is True


def test_ready_to_advance_one_is_enough():
    proc_eng = top.ProceduresEngine(None, branching_procedure_one_option(), 's1')

    assert proc_eng.ready_to_advance() is True


def test_ready_to_advance_no_options():
    proc_eng = top.ProceduresEngine(None, branching_procedure_no_options(), 's1')

    assert proc_eng.ready_to_advance() is False


def test_next_step_immediate():
    plumb_eng = one_component_engine()
    proc_eng = top.ProceduresEngine(plumb_eng, linear_procedure(), 's1')

    assert proc_eng.current_step.step_id == 's1'
    assert plumb_eng.current_state('c1') == 'closed'
    proc_eng.next_step()
    assert proc_eng.current_step.step_id == 's2'
    assert plumb_eng.current_state('c1') == 'open'
    proc_eng.next_step()
    assert proc_eng.current_step.step_id == 's3'
    assert plumb_eng.current_state('c1') == 'closed'


def test_next_step_requires_satisfaction():
    plumb_eng = one_component_engine()
    proc_eng = top.ProceduresEngine(plumb_eng, branching_procedure_no_options(), 's1')

    assert proc_eng.current_step.step_id == 's1'
    assert plumb_eng.current_state('c1') == 'closed'
    proc_eng.next_step()
    assert proc_eng.current_step.step_id == 's1'
    assert plumb_eng.current_state('c1') == 'closed'


def test_next_step_follows_satisfied_condition():
    plumb_eng = one_component_engine()
    proc_eng = top.ProceduresEngine(plumb_eng, branching_procedure_one_option(), 's1')

    assert proc_eng.current_step.step_id == 's1'
    assert plumb_eng.current_state('c1') == 'closed'
    proc_eng.next_step()
    assert proc_eng.current_step.step_id == 's3'
    assert plumb_eng.current_state('c1') == 'open'


def test_next_step_follows_highest_priority_condition():
    plumb_eng = one_component_engine()
    proc_eng = top.ProceduresEngine(plumb_eng, branching_procedure_two_options(), 's1')

    assert proc_eng.current_step.step_id == 's1'
    assert plumb_eng.current_state('c1') == 'closed'
    proc_eng.next_step()
    assert proc_eng.current_step.step_id == 's2'
    assert plumb_eng.current_state('c1') == 'halfway_open'
