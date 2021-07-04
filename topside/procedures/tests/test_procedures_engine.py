import copy

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

    initial_states = {'c1': 'open'}

    return top.PlumbingEngine({'c1': c1}, mapping, pressures, initial_states)


def single_procedure_suite():
    close_action = top.StateChangeAction('c1', 'closed')
    open_action = top.StateChangeAction('c1', 'open')

    s1 = top.ProcedureStep('s1', close_action, [(
        top.Immediate(), top.Transition('p1', 's2'))], 'PRIMARY')
    s2 = top.ProcedureStep('s2', open_action, [], 'PRIMARY')

    proc = top.Procedure('p1', [s1, s2])

    return top.ProcedureSuite([proc], 'p1')


def branching_procedure_suite_no_options():
    close_action = top.StateChangeAction('c1', 'closed')
    open_action = top.StateChangeAction('c1', 'open')
    halfway_open_action = top.StateChangeAction('c1', 'halfway_open')

    s1 = top.ProcedureStep('s1', close_action, [
        (NeverSatisfied(), top.Transition('p1', 's2')),
        (NeverSatisfied(), top.Transition('p2', 's3'))], 'PRIMARY')
    s2 = top.ProcedureStep('s2', halfway_open_action, [], 'PRIMARY')
    s3 = top.ProcedureStep('s3', open_action, [], 'PRIMARY')

    proc_1 = top.Procedure('p1', [s1, s2, s3])
    proc_2 = top.Procedure('p2', [s1, s2, s3])

    return top.ProcedureSuite([proc_1, proc_2], 'p1')


def branching_procedure_suite_one_option():
    close_action = top.StateChangeAction('c1', 'closed')
    open_action = top.StateChangeAction('c1', 'open')
    halfway_open_action = top.StateChangeAction('c1', 'halfway_open')

    s1 = top.ProcedureStep('s1', close_action, [
        (NeverSatisfied(), top.Transition('p1', 's2')),
        (top.Immediate(), top.Transition('p2', 's3'))], 'PRIMARY')
    s2 = top.ProcedureStep('s2', halfway_open_action, {}, 'PRIMARY')
    s3 = top.ProcedureStep('s3', open_action, {}, 'PRIMARY')

    proc_1 = top.Procedure('p1', [s1, s2, s3])
    proc_2 = top.Procedure('p2', [s1, s2, s3])

    return top.ProcedureSuite([proc_1, proc_2], 'p1')


def branching_procedure_suite_two_options():
    close_action = top.StateChangeAction('c1', 'closed')
    open_action = top.StateChangeAction('c1', 'open')
    halfway_open_action = top.StateChangeAction('c1', 'halfway_open')

    s1 = top.ProcedureStep('s1', close_action, [
        (top.Immediate(), top.Transition('p1', 's2')),
        (top.Immediate(), top.Transition('p2', 's3'))], 'PRIMARY')
    s2 = top.ProcedureStep('s2', halfway_open_action, {}, 'PRIMARY')
    s3 = top.ProcedureStep('s3', open_action, {}, 'PRIMARY')

    proc_1 = top.Procedure('p1', [s1, s2, s3])
    proc_2 = top.Procedure('p2', [s1, s2, s3])

    return top.ProcedureSuite([proc_1, proc_2], 'p1')


def test_load_suite():
    p1s1 = top.ProcedureStep('p1s1', top.StateChangeAction('injector_valve', 'open'), [], 'PRIMARY')
    suite_1 = top.ProcedureSuite([top.Procedure('p1', [p1s1])], 'p1')

    p2s1 = top.ProcedureStep('p2s1', top.StateChangeAction('injector_valve', 'closed'), [],
                             'SECONDARY')
    suite_2 = top.ProcedureSuite([top.Procedure('p2', [p2s1])], 'p2')

    proc_eng = top.ProceduresEngine(None, suite_1)

    assert proc_eng._suite == suite_1
    assert proc_eng.current_procedure_id == 'p1'
    assert proc_eng.current_step == p1s1
    assert proc_eng.step_position == top.StepPosition.Before

    proc_eng.load_suite(suite_2)

    assert proc_eng._suite == suite_2
    assert proc_eng.current_procedure_id == 'p2'
    assert proc_eng.current_step == p2s1
    assert proc_eng.step_position == top.StepPosition.Before


def test_execute_custom_action():
    plumb_eng = one_component_engine()
    proc_eng = top.ProceduresEngine(plumb_eng)

    action = top.StateChangeAction('c1', 'closed')

    assert plumb_eng.current_state('c1') == 'open'
    proc_eng.execute(action)
    assert plumb_eng.current_state('c1') == 'closed'

    misc_action = top.MiscAction('Approach the tower')
    proc_eng.execute(misc_action)
    assert plumb_eng.current_state('c1') == 'closed'


def test_execute_current():
    plumb_eng = one_component_engine()
    proc_eng = top.ProceduresEngine(plumb_eng, single_procedure_suite())

    assert proc_eng.current_step.step_id == 's1'
    assert proc_eng.step_position == top.StepPosition.Before
    assert plumb_eng.current_state('c1') == 'open'

    proc_eng.execute_current()

    assert proc_eng.current_step.step_id == 's1'
    assert proc_eng.step_position == top.StepPosition.After
    assert plumb_eng.current_state('c1') == 'closed'

    proc_eng.execute_current()  # No effect; engine is in a post-node

    assert proc_eng.current_step.step_id == 's1'
    assert proc_eng.step_position == top.StepPosition.After
    assert plumb_eng.current_state('c1') == 'closed'


def test_ready_to_proceed_requires_post():
    proc_eng = top.ProceduresEngine(None, single_procedure_suite())

    assert proc_eng.ready_to_proceed() is False


def test_ready_to_proceed_if_condition_satisfied():
    proc_eng = top.ProceduresEngine(None, single_procedure_suite())
    proc_eng.execute_current()

    assert proc_eng.ready_to_proceed() is True


def test_ready_to_proceed_one_is_enough():
    proc_eng = top.ProceduresEngine(None, branching_procedure_suite_one_option())
    proc_eng.execute_current()

    assert proc_eng.ready_to_proceed() is True


def test_ready_to_proceed_no_options():
    proc_eng = top.ProceduresEngine(None, branching_procedure_suite_no_options())
    proc_eng.execute_current()

    assert proc_eng.ready_to_proceed() is False


def test_proceed():
    plumb_eng = one_component_engine()
    proc_eng = top.ProceduresEngine(plumb_eng, single_procedure_suite())

    proc_eng.execute_current()

    assert proc_eng.current_step.step_id == 's1'
    assert proc_eng.step_position == top.StepPosition.After
    assert plumb_eng.current_state('c1') == 'closed'

    proc_eng.proceed()

    assert proc_eng.current_step.step_id == 's2'
    assert proc_eng.step_position == top.StepPosition.Before
    assert plumb_eng.current_state('c1') == 'closed'

    proc_eng.proceed()  # No effect; engine is in a pre-node

    assert proc_eng.current_step.step_id == 's2'
    assert proc_eng.step_position == top.StepPosition.Before
    assert plumb_eng.current_state('c1') == 'closed'


def test_proceed_requires_satisfaction():
    plumb_eng = one_component_engine()
    proc_eng = top.ProceduresEngine(plumb_eng, branching_procedure_suite_no_options())

    proc_eng.execute_current()
    proc_eng.proceed()

    assert proc_eng.current_procedure_id == 'p1'
    assert proc_eng.current_step.step_id == 's1'


def test_proceed_follows_satisfied_condition():
    plumb_eng = one_component_engine()
    proc_eng = top.ProceduresEngine(plumb_eng, branching_procedure_suite_one_option())

    proc_eng.execute_current()
    proc_eng.proceed()

    assert proc_eng.current_procedure_id == 'p2'
    assert proc_eng.current_step.step_id == 's3'


def test_proceed_follows_highest_priority_condition():
    plumb_eng = one_component_engine()
    proc_eng = top.ProceduresEngine(plumb_eng, branching_procedure_suite_two_options())

    proc_eng.execute_current()
    proc_eng.proceed()

    assert proc_eng.current_procedure_id == 'p1'
    assert proc_eng.current_step.step_id == 's2'


def test_next_step():
    plumb_eng = one_component_engine()
    proc_eng = top.ProceduresEngine(plumb_eng, single_procedure_suite())

    assert proc_eng.current_step.step_id == 's1'
    assert plumb_eng.current_state('c1') == 'open'
    proc_eng.next_step()
    assert proc_eng.current_step.step_id == 's1'
    assert plumb_eng.current_state('c1') == 'closed'
    proc_eng.next_step()
    assert proc_eng.current_step.step_id == 's2'
    assert plumb_eng.current_state('c1') == 'open'
    proc_eng.next_step()
    assert proc_eng.current_step.step_id == 's2'
    assert plumb_eng.current_state('c1') == 'open'


def test_transitions_respects_procedure_identifier():
    plumb_eng = one_component_engine()

    action = top.MiscAction('Do nothing')

    s1 = top.ProcedureStep('s1', action, [(NeverSatisfied(), top.Transition('p1', 'same_name')),
                                          (top.Immediate(), top.Transition('p2', 'same_name'))],
                           'PRIMARY')
    same_name_1 = top.ProcedureStep('same_name', action, [], 'PRIMARY')
    same_name_2 = top.ProcedureStep('same_name', action, [], 'PRIMARY')

    proc_1 = top.Procedure('p1', [s1, same_name_1])
    proc_2 = top.Procedure('p2', [same_name_2])
    proc_suite = top.ProcedureSuite([proc_1, proc_2], 'p1')

    proc_eng = top.ProceduresEngine(plumb_eng, proc_suite)
    proc_eng.execute_current()

    assert proc_eng.current_procedure_id == 'p1'
    assert proc_eng.current_step.step_id == 's1'
    proc_eng.next_step()
    assert proc_eng.current_procedure_id == 'p2'
    assert proc_eng.current_step.step_id == 'same_name'


def test_update_conditions_updates_pressures():
    plumb_eng = one_component_engine()
    plumb_eng.set_component_state('c1', 'open')

    s1 = top.ProcedureStep('s1', None, [(top.Less(1, 75), top.Transition('p1', 's2'))], 'PRIMARY')
    proc = top.Procedure('p1', [s1])
    proc_suite = top.ProcedureSuite([proc], 'p1')

    proc_eng = top.ProceduresEngine(plumb_eng, proc_suite)
    proc_eng.execute_current()

    assert proc_eng.ready_to_proceed() is False

    plumb_eng.solve()
    proc_eng.update_conditions()

    assert proc_eng.ready_to_proceed() is True


def test_update_conditions_updates_time():
    plumb_eng = one_component_engine()
    plumb_eng.set_component_state('c1', 'open')

    s1 = top.ProcedureStep('s1', None, [(top.WaitFor(10), 's2')], 'PRIMARY')
    proc = top.Procedure('p1', [s1])
    proc_suite = top.ProcedureSuite([proc], 'p1')

    proc_eng = top.ProceduresEngine(plumb_eng, proc_suite)
    proc_eng.execute_current()

    assert proc_eng.ready_to_proceed() is False

    plumb_eng.step(10)
    proc_eng.update_conditions()

    assert proc_eng.ready_to_proceed() is True


def test_step_advances_time_equally():
    managed_eng = one_component_engine()
    managed_eng.set_component_state('c1', 'open')

    unmanaged_eng = copy.deepcopy(managed_eng)

    proc_eng = top.ProceduresEngine(managed_eng, single_procedure_suite())

    assert managed_eng.current_pressures() == unmanaged_eng.current_pressures()

    proc_eng.step_time(1e6)
    unmanaged_eng.step(1e6)

    assert managed_eng.current_pressures() == unmanaged_eng.current_pressures()


def test_step_updates_conditions():
    plumb_eng = one_component_engine()
    plumb_eng.set_component_state('c1', 'open')

    s1 = top.ProcedureStep('s1', None, [(top.Less(1, 75), 's2')], 'PRIMARY')
    proc = top.Procedure('p1', [s1])
    proc_suite = top.ProcedureSuite([proc], 'p1')

    proc_eng = top.ProceduresEngine(plumb_eng, proc_suite)
    proc_eng.execute_current()

    assert proc_eng.ready_to_proceed() is False

    proc_eng.step_time(1e6)

    assert proc_eng.ready_to_proceed() is True


def test_reset():
    plumb_eng = one_component_engine()
    proc_eng = top.ProceduresEngine(plumb_eng, branching_procedure_suite_one_option())

    assert proc_eng.current_procedure_id == 'p1'
    assert proc_eng.current_step.step_id == 's1'
    assert plumb_eng.current_state('c1') == 'open'
    proc_eng.next_step()
    assert proc_eng.current_procedure_id == 'p1'
    assert proc_eng.current_step.step_id == 's1'
    assert plumb_eng.current_state('c1') == 'closed'
    proc_eng.next_step()
    assert proc_eng.current_procedure_id == 'p2'
    assert proc_eng.current_step.step_id == 's3'
    assert plumb_eng.current_state('c1') == 'open'
    proc_eng.reset()
    assert proc_eng.current_procedure_id == 'p1'
    assert proc_eng.current_step.step_id == 's1'
    assert plumb_eng.current_state('c1') == 'open'


def test_reset_clears_conditions():
    plumb_eng = one_component_engine()
    plumb_eng.set_component_state('c1', 'open')

    s1 = top.ProcedureStep('s1', None, [(top.WaitFor(10), 's2')], 'PRIMARY')
    proc = top.Procedure('p1', [s1])
    proc_suite = top.ProcedureSuite([proc], 'p1')

    proc_eng = top.ProceduresEngine(plumb_eng, proc_suite)
    proc_eng.execute_current()

    assert proc_eng.ready_to_proceed() is False

    plumb_eng.step(10)
    proc_eng.update_conditions()

    assert proc_eng.ready_to_proceed() is True

    proc_eng.reset()
    proc_eng.execute_current()

    assert proc_eng.ready_to_proceed() is False


def test_undo_1():
    plumb_eng = one_component_engine()
    proc_eng = top.ProceduresEngine(plumb_eng, branching_procedure_suite_one_option())

    assert proc_eng.current_procedure_id == 'p1'
    assert proc_eng.current_step.step_id == 's1'
    assert proc_eng._plumb.current_state('c1') == 'open'
    proc_eng.next_step()
    assert proc_eng.current_procedure_id == 'p1'
    assert proc_eng.current_step.step_id == 's1'
    assert plumb_eng.current_state('c1') == 'closed'
    proc_eng.next_step()
    assert proc_eng.current_procedure_id == 'p2'
    assert proc_eng.current_step.step_id == 's3'
    assert proc_eng._plumb.current_state('c1') == 'open'
    proc_eng.pop_and_set_stack()
    assert proc_eng.current_procedure_id == 'p1'
    assert proc_eng.current_step.step_id == 's1'
    assert proc_eng._plumb.current_state('c1') == 'closed'
    proc_eng.pop_and_set_stack()
    assert proc_eng.current_procedure_id == 'p1'
    assert proc_eng.current_step.step_id == 's1'
    assert proc_eng._plumb.current_state('c1') == 'open'


def test_undo_2():
    plumb_eng = one_component_engine()
    proc_eng = top.ProceduresEngine(plumb_eng, single_procedure_suite())

    assert proc_eng.current_step.step_id == 's1'
    assert plumb_eng.current_state('c1') == 'open'
    proc_eng.next_step()
    assert proc_eng.current_step.step_id == 's1'
    assert plumb_eng.current_state('c1') == 'closed'
    proc_eng.next_step()
    assert proc_eng.current_step.step_id == 's2'
    assert plumb_eng.current_state('c1') == 'open'
    proc_eng.next_step()
    assert proc_eng.current_step.step_id == 's2'
    assert plumb_eng.current_state('c1') == 'open'
    proc_eng.pop_and_set_stack()
    assert proc_eng.current_step.step_id == 's2'
    assert plumb_eng.current_state('c1') == 'open'
    proc_eng.pop_and_set_stack()
    assert proc_eng.current_step.step_id == 's1'
    assert plumb_eng.current_state('c1') == 'closed'
    proc_eng.pop_and_set_stack()
    assert proc_eng.current_step.step_id == 's1'
    assert plumb_eng.current_state('c1') == 'open'

def test_undo_3():
    ##This test is here largly to ensure the engine dosen't crash or do something wierd
    proc_eng = top.ProceduresEngine(None, single_procedure_suite())

    assert proc_eng._plumb == None
    proc_eng.next_step()

    proc_eng.pop_and_set_stack()
    assert proc_eng._plumb == None
