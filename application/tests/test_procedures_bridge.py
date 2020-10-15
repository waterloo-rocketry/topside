from PySide2.QtCore import QObject, Signal

import topside as top
from ..procedures_bridge import ProceduresBridge


class MockPlumbingBridge(QObject):
    engineLoaded = Signal(top.PlumbingEngine)

    def __init__(self):
        QObject.__init__(self)
        self.engine = None


def test_proc_bridge_init():
    plumb_b = MockPlumbingBridge()
    proc_b = ProceduresBridge(plumb_b)

    assert proc_b._proc_eng._suite is None
    assert proc_b._proc_steps.procedure is None


def test_proc_bridge_load_suite():
    plumb_b = MockPlumbingBridge()
    proc_b = ProceduresBridge(plumb_b)

    procedure = top.Procedure('main', [
        top.ProcedureStep('1', top.StateChangeAction('injector_valve', 'open'), [
            (top.Immediate(), top.Transition('main', '2'))], 'PRIMARY'),
        top.ProcedureStep('2', top.MiscAction('Approach the launch tower'), [], 'SECONDARY')
    ])

    suite = top.ProcedureSuite([procedure])

    proc_b.load_suite(suite)

    assert proc_b._proc_eng._suite == suite
    assert proc_b.steps.procedure == procedure


def test_proc_bridge_procedure_controls_advance_procedure():
    plumb_b = MockPlumbingBridge()
    proc_b = ProceduresBridge(plumb_b)

    procedure = top.Procedure('main', [
        top.ProcedureStep('1', top.StateChangeAction('injector_valve', 'open'), [
            (top.Immediate(), top.Transition('main', '2'))], 'PRIMARY'),
        top.ProcedureStep('2', top.StateChangeAction('vent_valve', 'closed'), [
            (top.WaitUntil(100), top.Transition('main', '3'))], 'PRIMARY'),
        top.ProcedureStep('3', top.MiscAction('Approach the launch tower'), [], 'SECONDARY')
    ])

    proc_b.load_suite(top.ProcedureSuite([procedure]))

    assert proc_b._proc_eng.current_step == procedure.step_list[0]
    proc_b.procStepForward()
    assert proc_b._proc_eng.current_step == procedure.step_list[1]
    proc_b.procStepForward()  # does nothing; condition is not satisfied
    assert proc_b._proc_eng.current_step == procedure.step_list[1]
    proc_b.procStop()
    assert proc_b._proc_eng.current_step == procedure.step_list[0]
