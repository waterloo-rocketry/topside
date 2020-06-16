import copy

import pytest

import topside as top
from topside.procedures.tests.testing_utils import NeverSatisfied


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

    pressures = {1: (100, False), 2: (0, False)}

    initial_states = {'c1': 'closed'}

    return top.PlumbingEngine({'c1': c1}, mapping, pressures, initial_states)


def single_procedure_suite():
    open_action = top.Action('c1', 'open')
    close_action = top.Action('c1', 'closed')

    s1 = top.ProcedureStep('s1', None, {top.Immediate(): top.Transition('p1', 's2')})
    s2 = top.ProcedureStep('s2', open_action, {top.Immediate(): top.Transition('p1', 's3')})
    s3 = top.ProcedureStep('s3', close_action, {})

    proc = top.Procedure('p1', {'s1': s1, 's2': s2, 's3': s3})

    return {'p1': proc}


def branching_procedure_suite_no_options():
    open_action = top.Action('c1', 'open')
    halfway_open_action = top.Action('c1', 'halfway_open')

    s1 = top.ProcedureStep('s1', None, {NeverSatisfied(): top.Transition('p1', 's2'),
                                        NeverSatisfied(): top.Transition('p2', 's3')})
    s2 = top.ProcedureStep('s2', halfway_open_action, {})
    s3 = top.ProcedureStep('s3', open_action, {})

    proc_1 = top.Procedure('p1', {'s1': s1, 's2': s2, 's3': s3})
    proc_2 = top.Procedure('p2', {'s1': s1, 's2': s2, 's3': s3})

    return {'p1': proc_1, 'p2': proc_2}


def branching_procedure_suite_one_option():
    open_action = top.Action('c1', 'open')
    halfway_open_action = top.Action('c1', 'halfway_open')

    s1 = top.ProcedureStep('s1', None, {NeverSatisfied(): top.Transition('p1', 's2'),
                                        top.Immediate(): top.Transition('p2', 's3')})
    s2 = top.ProcedureStep('s2', halfway_open_action, {})
    s3 = top.ProcedureStep('s3', open_action, {})

    proc_1 = top.Procedure('p1', {'s1': s1, 's2': s2, 's3': s3})
    proc_2 = top.Procedure('p2', {'s1': s1, 's2': s2, 's3': s3})

    return {'p1': proc_1, 'p2': proc_2}


def branching_procedure_suite_two_options():
    open_action = top.Action('c1', 'open')
    halfway_open_action = top.Action('c1', 'halfway_open')

    s1 = top.ProcedureStep('s1', None, {top.Immediate(): top.Transition('p1', 's2'),
                                        top.Immediate(): top.Transition('p2', 's3')})
    s2 = top.ProcedureStep('s2', halfway_open_action, {})
    s3 = top.ProcedureStep('s3', open_action, {})

    proc_1 = top.Procedure('p1', {'s1': s1, 's2': s2, 's3': s3})
    proc_2 = top.Procedure('p2', {'s1': s1, 's2': s2, 's3': s3})

    return {'p1': proc_1, 'p2': proc_2}


def test_execute_custom_action():
    plumb_eng = one_component_engine()
    proc_eng = top.ProceduresEngine(plumb_eng)

    action = top.Action('c1', 'open')

    assert plumb_eng.current_state('c1') == 'closed'
    proc_eng.execute(action)
    assert plumb_eng.current_state('c1') == 'open'


def test_ready_to_advance_if_condition_satisfied():
    proc_eng = top.ProceduresEngine(None, single_procedure_suite(), 'p1', 's1')

    assert proc_eng.ready_to_advance() is True


def test_ready_to_advance_one_is_enough():
    proc_eng = top.ProceduresEngine(None, branching_procedure_suite_one_option(), 'p1', 's1')

    assert proc_eng.ready_to_advance() is True


def test_ready_to_advance_no_options():
    proc_eng = top.ProceduresEngine(None, branching_procedure_suite_no_options(), 'p1', 's1')

    assert proc_eng.ready_to_advance() is False


def test_next_step_immediate():
    plumb_eng = one_component_engine()
    proc_eng = top.ProceduresEngine(plumb_eng, single_procedure_suite(), 'p1', 's1')

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
    proc_eng = top.ProceduresEngine(plumb_eng, branching_procedure_suite_no_options(), 'p1', 's1')

    assert proc_eng.current_procedure_id == 'p1'
    assert proc_eng.current_step.step_id == 's1'
    assert plumb_eng.current_state('c1') == 'closed'
    proc_eng.next_step()
    assert proc_eng.current_procedure_id == 'p1'
    assert proc_eng.current_step.step_id == 's1'
    assert plumb_eng.current_state('c1') == 'closed'


def test_next_step_follows_satisfied_condition():
    plumb_eng = one_component_engine()
    proc_eng = top.ProceduresEngine(plumb_eng, branching_procedure_suite_one_option(), 'p1', 's1')

    assert proc_eng.current_procedure_id == 'p1'
    assert proc_eng.current_step.step_id == 's1'
    assert plumb_eng.current_state('c1') == 'closed'
    proc_eng.next_step()
    assert proc_eng.current_procedure_id == 'p2'
    assert proc_eng.current_step.step_id == 's3'
    assert plumb_eng.current_state('c1') == 'open'


def test_next_step_follows_highest_priority_condition():
    plumb_eng = one_component_engine()
    proc_eng = top.ProceduresEngine(plumb_eng, branching_procedure_suite_two_options(), 'p1', 's1')

    assert proc_eng.current_procedure_id == 'p1'
    assert proc_eng.current_step.step_id == 's1'
    assert plumb_eng.current_state('c1') == 'closed'
    proc_eng.next_step()
    assert proc_eng.current_procedure_id == 'p1'
    assert proc_eng.current_step.step_id == 's2'
    assert plumb_eng.current_state('c1') == 'halfway_open'


def test_transitions_respects_procedure_identifier():
    plumb_eng = one_component_engine()

    action = top.Action('c1', 'open')

    s1 = top.ProcedureStep('s1', None, {NeverSatisfied(): top.Transition('p1', 'same_name'),
                                        top.Immediate(): top.Transition('p2', 'same_name')})
    same_name_1 = top.ProcedureStep('same_name', action, {})
    same_name_2 = top.ProcedureStep('same_name', action, {})

    proc_1 = top.Procedure('p1', {'s1': s1, 'same_name': same_name_1})
    proc_2 = top.Procedure('p1', {'same_name': same_name_2})
    proc_suite = {'p1': proc_1, 'p2': proc_2}

    proc_eng = top.ProceduresEngine(plumb_eng, proc_suite, 'p1', 's1')

    assert proc_eng.current_procedure_id == 'p1'
    assert proc_eng.current_step.step_id == 's1'
    proc_eng.next_step()
    assert proc_eng.current_procedure_id == 'p2'
    assert proc_eng.current_step.step_id == 'same_name'


def test_update_conditions_updates_pressures():
    plumb_eng = one_component_engine()
    plumb_eng.set_component_state('c1', 'open')

    s1 = top.ProcedureStep('s1', None, {top.Less(1, 75): top.Transition('p1', 's2')})
    proc = top.Procedure('p1', {'s1': s1})
    proc_suite = {'p1': proc}

    proc_eng = top.ProceduresEngine(plumb_eng, proc_suite, 'p1', 's1')

    assert proc_eng.ready_to_advance() is False

    plumb_eng.solve()
    proc_eng.update_conditions()

    assert proc_eng.ready_to_advance() is True


def test_update_conditions_updates_time():
    plumb_eng = one_component_engine()
    plumb_eng.set_component_state('c1', 'open')

    s1 = top.ProcedureStep('s1', None, {top.WaitUntil(1e6): 's2'})
    proc = top.Procedure('p1', {'s1': s1})
    proc_suite = {'p1': proc}

    proc_eng = top.ProceduresEngine(plumb_eng, proc_suite, 'p1', 's1')

    assert proc_eng.ready_to_advance() is False

    plumb_eng.step(1e6 - 1)
    proc_eng.update_conditions()

    assert proc_eng.ready_to_advance() is False

    plumb_eng.step(1)
    proc_eng.update_conditions()

    assert proc_eng.ready_to_advance() is True


def test_step_advances_time_equally():
    managed_eng = one_component_engine()
    managed_eng.set_component_state('c1', 'open')

    unmanaged_eng = copy.deepcopy(managed_eng)

    proc_eng = top.ProceduresEngine(managed_eng, single_procedure_suite(), 'p1', 's1')

    assert managed_eng.current_pressures() == unmanaged_eng.current_pressures()

    proc_eng.step(1e6)
    unmanaged_eng.step(1e6)

    assert managed_eng.current_pressures() == unmanaged_eng.current_pressures()


def test_step_updates_conditions():
    plumb_eng = one_component_engine()
    plumb_eng.set_component_state('c1', 'open')

    s1 = top.ProcedureStep('s1', None, {top.Less(1, 75): 's2'})
    proc = top.Procedure('p1', {'s1': s1})
    proc_suite = {'p1': proc}

    proc_eng = top.ProceduresEngine(plumb_eng, proc_suite, 'p1', 's1')

    assert proc_eng.ready_to_advance() is False

    proc_eng.step(1e6)

    assert proc_eng.ready_to_advance() is True
