from PySide2.QtCore import QObject, Signal

import topside as top
from ..procedures_bridge import ProceduresBridge
from ..controls_bridge import ControlsBridge


class MockPlumbingBridge(QObject):
    engineLoaded = Signal(top.PlumbingEngine)
    dataUpdated = Signal()

    def __init__(self):
        QObject.__init__(self)
        self.engine = None


def test_proc_bridge_init():
    plumb_b = MockPlumbingBridge()
    control_b = ControlsBridge(plumb_b)
    proc_b = ProceduresBridge(plumb_b, control_b)

    assert proc_b._proc_eng._suite is None
    assert proc_b._proc_steps.procedure is None


def test_proc_bridge_load_suite():
    plumb_b = MockPlumbingBridge()
    control_b = ControlsBridge(plumb_b)
    proc_b = ProceduresBridge(plumb_b, control_b)

    procedure = top.Procedure('main', [
        top.ProcedureStep('1', top.StateChangeAction('injector_valve', 'open'), [
            (top.Immediate(), top.Transition('main', '2'))], 'PRIMARY'),
        top.ProcedureStep('2', top.MiscAction('Approach the launch tower'), [], 'SECONDARY')
    ])

    suite = top.ProcedureSuite([procedure])

    proc_b.load_suite(suite)

    assert proc_b._proc_eng._suite == suite
    assert proc_b.steps.procedure == procedure
