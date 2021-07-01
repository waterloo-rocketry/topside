import textwrap

import topside as top
from ..procedures_bridge import ProceduresBridge
from ..plumbing_bridge import PlumbingBridge
from ..controls_bridge import ControlsBridge


def make_plumbing_engine():
    pdl = textwrap.dedent("""\
    name: example

    body:
    - component:
        name: injector_valve
        edges:
          edge1:
              nodes: [A, B]
        states:
          open:
              edge1: 1
          closed:
              edge1: closed
    - graph:
        name: main
        nodes:
          A:
            initial_pressure: 100
            components:
              - [injector_valve, A]
          B:
            initial_pressure: 0
            components:
              - [injector_valve, B]
        states:
          injector_valve: closed
    """)
    parser = top.Parser(pdl, 's')
    return parser.make_engine()


def test_proc_bridge_procedure_step_affects_plumbing():
    plumb_b = PlumbingBridge()
    control_b = ControlsBridge(plumb_b)
    proc_b = ProceduresBridge(plumb_b, control_b)

    procedure = top.Procedure('main', [
        top.ProcedureStep('1', top.StateChangeAction('injector_valve', 'open'), [
            (top.Immediate(), top.Transition('main', '2'))], 'PRIMARY'),
        top.ProcedureStep('2', top.StateChangeAction('injector_valve', 'closed'), [
            (top.Immediate(), top.Transition('main', '3'))], 'PRIMARY'),
        top.ProcedureStep('3', top.MiscAction('Approach the launch tower'), [], 'SECONDARY')
    ])
    proc_b.load_suite(top.ProcedureSuite([procedure]))

    plumb_eng = make_plumbing_engine()
    plumb_b.load_engine(plumb_eng)

    assert plumb_eng.current_state('injector_valve') == 'closed'
    proc_b.procStepForward()
    assert plumb_eng.current_state('injector_valve') == 'open'
    proc_b.procStepForward()
    assert plumb_eng.current_state('injector_valve') == 'closed'


def test_time_step_forward():
    plumb_b = PlumbingBridge()
    plumb_b.step_size = 0.1e6
    control_b = ControlsBridge(plumb_b)
    proc_b = ProceduresBridge(plumb_b, control_b)

    procedure = top.Procedure('main', [
        top.ProcedureStep('1', top.StateChangeAction('injector_valve', 'open'), [
            (top.WaitFor(0.2e6), top.Transition('main', '2'))], 'PRIMARY'),
        top.ProcedureStep('2', top.StateChangeAction('injector_valve', 'closed'), [
            (top.WaitFor(0.2e6), top.Transition('main', '3'))], 'PRIMARY'),
        top.ProcedureStep('3', top.MiscAction('Approach the launch tower'), [], 'SECONDARY')
    ])
    proc_b.load_suite(top.ProcedureSuite([procedure]))

    plumb_eng = make_plumbing_engine()
    plumb_b.load_engine(plumb_eng)

    proc_eng = proc_b._proc_eng

    proc_b.procStepForward()  # execute step 1
    assert not proc_eng.ready_to_proceed()
    # Time hasn't advanced yet, so pressures should be the same
    assert plumb_eng.current_pressures('A') == 100
    assert plumb_eng.current_pressures('B') == 0

    plumb_b.timeStepForward()  # time == 0.1s
    assert not proc_eng.ready_to_proceed()
    # Valve is open, so pressures should start dropping
    assert plumb_eng.current_pressures('A') < 100
    assert plumb_eng.current_pressures('B') > 0

    plumb_b.timeStepForward()  # time == 0.2s
    assert proc_eng.ready_to_proceed()
    pressures_at_02 = plumb_eng.current_pressures()

    proc_b.procStepForward()  # execute step 2
    assert not proc_eng.ready_to_proceed()
    assert plumb_eng.current_pressures() == pressures_at_02

    plumb_b.timeStepForward()  # time == 0.3s
    assert not proc_eng.ready_to_proceed()
    # Valve is now closed, so pressures shouldn't change further
    assert plumb_eng.current_pressures() == pressures_at_02


def test_time_advance():
    plumb_b = PlumbingBridge()
    control_b = ControlsBridge(plumb_b)
    proc_b = ProceduresBridge(plumb_b, control_b)

    procedure = top.Procedure('main', [
        top.ProcedureStep('1', top.StateChangeAction('injector_valve', 'open'), [
            (top.Less('A', 75), top.Transition('main', '2'))], 'PRIMARY'),
        top.ProcedureStep('2', top.MiscAction('Approach the launch tower'), [], 'SECONDARY')
    ])
    proc_b.load_suite(top.ProcedureSuite([procedure]))

    plumb_eng = make_plumbing_engine()
    plumb_b.load_engine(plumb_eng)

    tol = 0.01

    proc_eng = proc_b._proc_eng

    proc_b.procStepForward()  # execute step 1
    assert not proc_eng.ready_to_proceed()
    assert plumb_eng.current_pressures('A') == 100
    assert plumb_eng.current_pressures('B') == 0

    plumb_b.timeAdvance()
    assert proc_eng.ready_to_proceed()
    # We expect pressures to equalize at 50 once the system is steady
    assert abs(plumb_eng.current_pressures('A') - 50) < tol
    assert abs(plumb_eng.current_pressures('B') - 50) < tol


def test_time_stop():
    plumb_b = PlumbingBridge()
    plumb_b.step_size = 0.1e6
    control_b = ControlsBridge(plumb_b)
    proc_b = ProceduresBridge(plumb_b, control_b)

    procedure = top.Procedure('main', [
        top.ProcedureStep('1', top.StateChangeAction('injector_valve', 'open'), [
            (top.WaitFor(0.1e6), top.Transition('main', '2'))], 'PRIMARY'),
        top.ProcedureStep('2', top.MiscAction('Approach the launch tower'), [], 'SECONDARY')
    ])
    proc_b.load_suite(top.ProcedureSuite([procedure]))

    plumb_eng = make_plumbing_engine()
    plumb_b.load_engine(plumb_eng)

    proc_eng = proc_b._proc_eng

    proc_b.procStepForward()  # execute step 1
    assert not proc_eng.ready_to_proceed()
    # Time hasn't advanced yet, so pressures should be the same
    assert plumb_eng.current_pressures('A') == 100
    assert plumb_eng.current_pressures('B') == 0

    plumb_b.timeStepForward()  # time == 0.1s
    assert proc_eng.ready_to_proceed()
    # Valve is open, so pressures should start dropping
    assert plumb_eng.current_pressures('A') < 100
    assert plumb_eng.current_pressures('B') > 0

    proc_b.procStop()
    plumb_b.timeStop()

    # Everything should now be as it started

    assert proc_eng.current_step.step_id == '1'
    assert plumb_eng.current_state('injector_valve') == 'closed'
    assert plumb_eng.current_pressures('A') == 100
    assert plumb_eng.current_pressures('B') == 0

    proc_b.procStepForward()  # execute step 1
    assert not proc_eng.ready_to_proceed()
    # Time hasn't advanced yet, so pressures should be the same
    assert plumb_eng.current_pressures('A') == 100
    assert plumb_eng.current_pressures('B') == 0

    plumb_b.timeStepForward()  # time == 0.1s
    assert proc_eng.ready_to_proceed()
    # Valve is open, so pressures should start dropping
    assert plumb_eng.current_pressures('A') < 100
    assert plumb_eng.current_pressures('B') > 0


def test_jump_to_step_normal():
    plumb_b = PlumbingBridge()
    control_b = ControlsBridge(plumb_b)
    proc_b = ProceduresBridge(plumb_b, control_b)

    procedure = top.Procedure('main', [
        top.ProcedureStep('1', top.StateChangeAction('injector_valve', 'open'), [
            (top.Immediate(), top.Transition('main', '2'))], 'PRIMARY'),
        top.ProcedureStep('2', top.StateChangeAction('injector_valve', 'closed'), [
            (top.Immediate(), top.Transition('main', '3'))], 'PRIMARY'),
        top.ProcedureStep('3', top.StateChangeAction('injector_valve', 'closed'), [
            (top.Immediate(), top.Transition('main', '4'))], 'PRIMARY'),
        top.ProcedureStep('4', top.MiscAction('Approach the launch tower'), [], 'SECONDARY')
    ])

    proc_b.load_suite(top.ProcedureSuite([procedure]))

    plumb_eng = make_plumbing_engine()
    plumb_b.load_engine(plumb_eng)

    proc_eng = proc_b._proc_eng

    assert proc_eng.current_step == procedure.step_list[0]
    assert proc_eng.step_position == top.StepPosition.Before
    proc_b.procJump("2")
    assert proc_eng.current_step == procedure.step_list[1]
    assert proc_eng.step_position == top.StepPosition.After
    proc_b.procJump("4")
    assert proc_eng.current_step == procedure.step_list[3]
    assert proc_eng.step_position == top.StepPosition.After


def test_jump_to_step_current_and_past():
    plumb_b = PlumbingBridge()
    control_b = ControlsBridge(plumb_b)
    proc_b = ProceduresBridge(plumb_b, control_b)

    procedure = top.Procedure('main', [
        top.ProcedureStep('1', top.StateChangeAction('injector_valve', 'open'), [
            (top.Immediate(), top.Transition('main', '2'))], 'PRIMARY'),
        top.ProcedureStep('2', top.StateChangeAction('injector_valve', 'closed'), [
            (top.Immediate(), top.Transition('main', '3'))], 'PRIMARY'),
        top.ProcedureStep('3', top.StateChangeAction('injector_valve', 'closed'), [
            (top.Immediate(), top.Transition('main', '4'))], 'PRIMARY'),
        top.ProcedureStep('4', top.MiscAction('Approach the launch tower'), [], 'SECONDARY')
    ])

    proc_b.load_suite(top.ProcedureSuite([procedure]))

    plumb_eng = make_plumbing_engine()
    plumb_b.load_engine(plumb_eng)

    proc_eng = proc_b._proc_eng

    assert proc_eng.current_step == procedure.step_list[0]
    assert proc_eng.step_position == top.StepPosition.Before
    proc_b.procJump("1")  # jumping to a current step; does nothing
    assert proc_eng.current_step == procedure.step_list[0]
    assert proc_eng.step_position == top.StepPosition.Before
    proc_b.procJump("3")
    assert proc_eng.current_step == procedure.step_list[2]
    assert proc_eng.step_position == top.StepPosition.After
    proc_b.procJump("2")  # attemping to jump to a past step; does nothing
    assert proc_eng.current_step == procedure.step_list[2]
    assert proc_eng.step_position == top.StepPosition.After


def test_jump_to_step_invalid():
    plumb_b = PlumbingBridge()
    control_b = ControlsBridge(plumb_b)
    proc_b = ProceduresBridge(plumb_b, control_b)

    procedure = top.Procedure('main', [
        top.ProcedureStep('1', top.StateChangeAction('injector_valve', 'open'), [
            (top.Immediate(), top.Transition('main', '2'))], 'PRIMARY'),
        top.ProcedureStep('2', top.StateChangeAction('injector_valve', 'closed'), [
            (top.Immediate(), top.Transition('main', '3'))], 'PRIMARY'),
        top.ProcedureStep('3', top.StateChangeAction('injector_valve', 'closed'), [
            (top.Immediate(), top.Transition('main', '4'))], 'PRIMARY'),
        top.ProcedureStep('4', top.MiscAction('Approach the launch tower'), [], 'SECONDARY')
    ])

    proc_b.load_suite(top.ProcedureSuite([procedure]))

    plumb_eng = make_plumbing_engine()
    plumb_b.load_engine(plumb_eng)

    proc_eng = proc_b._proc_eng

    assert proc_eng.current_step == procedure.step_list[0]
    assert proc_eng.step_position == top.StepPosition.Before
    proc_b.procJump("-1")
    assert proc_eng.current_step == procedure.step_list[0]
    assert proc_eng.step_position == top.StepPosition.Before
    proc_b.procJump("test")
    assert proc_eng.current_step == procedure.step_list[0]
    assert proc_eng.step_position == top.StepPosition.Before
    proc_b.procJump("0")
    assert proc_eng.current_step == procedure.step_list[0]
    assert proc_eng.step_position == top.StepPosition.Before
    proc_b.procJump("3")
    assert proc_eng.current_step == procedure.step_list[2]
    assert proc_eng.step_position == top.StepPosition.After
    proc_b.procJump("10")
    assert proc_eng.current_step == procedure.step_list[2]
    assert proc_eng.step_position == top.StepPosition.After
