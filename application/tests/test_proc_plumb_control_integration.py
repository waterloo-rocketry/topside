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

def test_control_panel_initialization():
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
  control_b.refresh()
  assert(control_b.toggleable_components == ['injector_valve'])
  assert(control_b.isOpen[0] == False)

def test_procedure_step_affects_component_state():
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
  control_b.refresh()
  proc_eng = proc_b._proc_eng

  assert proc_eng.current_step == procedure.step_list[0]
  assert proc_eng.step_position == top.StepPosition.Before
  proc_b.procStepForward()

  assert(control_b.isOpen[0] == True)
  assert proc_eng.current_step == procedure.step_list[0]
  assert proc_eng.step_position == top.StepPosition.After

  proc_b.procStepForward()
  assert(control_b.isOpen[0] == False)
  assert proc_eng.current_step == procedure.step_list[1]
  assert proc_eng.step_position == top.StepPosition.After

  proc_b.procStepForward()
  assert(control_b.isOpen[0] == False)

  proc_b.procStop()
  assert proc_eng.current_step == procedure.step_list[0]
  assert proc_eng.step_position == top.StepPosition.Before

def test_control_panel_affects_plumbing_engine():
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
  control_b.refresh()
  control_b.set_component_states(0, 'open')
  assert(plumb_eng.current_state('injector_valve') == 'open')
  control_b.set_component_states(0, 'closed')
  assert(plumb_eng.current_state('injector_valve') == 'closed')