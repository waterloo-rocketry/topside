from PySide2.QtCore import Slot, Signal, Property, QObject
from PySide2.QtWidgets import QFileDialog

import topside as top
from .procedure_wrappers import ProcedureStepsModel


class ProceduresBridge(QObject):
    goto_step_sig = Signal(int, name='gotoStep')
    steps_changed_sig = Signal(name='dataChanged')

    def __init__(self, plumb):
        QObject.__init__(self)

        self._plumb = plumb
        self._proc_eng = top.ProceduresEngine(self._plumb.engine)
        self._plumb.engineLoaded.connect(self.updatePlumbingEngine)

        self._proc_steps = ProcedureStepsModel()
        self._refresh_procedure_view()

    def _refresh_procedure_view(self):
        proc = self._proc_eng.current_procedure()
        displayed_proc = self._proc_steps.procedure

        if proc is None:
            self._proc_steps.change_procedure(None)
            return

        if displayed_proc != proc:
            self._proc_steps.change_procedure(proc)

        idx = proc.index_of(self._proc_eng.current_step.step_id)
        self.goto_step_sig.emit(idx)

        self._proc_steps.refresh(idx)

    def load_suite(self, suite):
        self._proc_eng.load_suite(suite)
        self._refresh_procedure_view()

    def load_from_file(self, filepath):
        with open(filepath) as f:
            proclang = f.read()
        suite = top.proclang.parse(proclang)
        self.load_suite(suite)

    @Property(QObject, notify=steps_changed_sig)
    def steps(self):
        return self._proc_steps

    @Slot()
    def loadFromDialog(self):
        # TODO(jacob): Make this menu remember the last file opened
        filepath, _ = QFileDialog.getOpenFileName(self.parent(), 'Load ProcLang file')
        if filepath != '':
            self.load_from_file(filepath)

    # Procedure controls

    @Slot(top.PlumbingEngine)
    def updatePlumbingEngine(self, engine):
        self._proc_eng._plumb = engine

    @Slot()
    def procPlayBackwards(self):
        pass

    @Slot()
    def procUndo(self):
        pass

    @Slot()
    def procPlay(self):
        pass

    @Slot()
    def procPause(self):
        pass

    @Slot()
    def procStop(self):
        # TODO(jacob): Should this reset the plumbing engine as well?
        self._proc_eng.reset()
        self._refresh_procedure_view()

    @Slot()
    def procStepForward(self):
        self._proc_eng.next_step()
        self._refresh_procedure_view()

    @Slot()
    def procAdvance(self):
        pass

    # Time controls

    @Slot()
    def timePlayBackwards(self):
        pass

    @Slot()
    def timeStepBackwards(self):
        pass

    @Slot()
    def timePlay(self):
        # TODO(jacob): Implement real-time simulation.
        pass

    @Slot()
    def timePause(self):
        pass

    @Slot()
    def timeStop(self):
        pass

    @Slot()
    def timeStepForward(self):
        step_size = 0.1e6  # TODO(jacob): Add a UI field for this.
        self._proc_eng.step_time(step_size)
        self._refresh_procedure_view()

    @Slot()
    def timeAdvance(self):
        self._plumb.engine.solve()
        self._proc_eng.update_conditions()
        self._refresh_procedure_view()
