import textwrap

import topside as top
from ..procedures_bridge import ProceduresBridge
from ..plumbing_bridge import PlumbingBridge


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
    proc_b = ProceduresBridge(plumb_b)

    procedure = top.Procedure('main', [
        top.ProcedureStep('0', top.MiscAction('Start of operations'), [
            (top.Immediate(), top.Transition('main', '1'))], 'OPS'),
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
