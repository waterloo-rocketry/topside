from PySide2.QtCore import Qt, Slot, Signal, Property, \
    QObject, QAbstractListModel, QModelIndex
from PySide2.QtWidgets import QFileDialog

import topside as top


class ProcedureConditionWrapper(QObject):
    satisfied_changed_signal = Signal(name='satisfiedChanged')

    def __init__(self, condition, transition, parent=None):
        QObject.__init__(self, parent=parent)
        self._condition = condition
        self._transition = transition

    # TODO(jacob): Make sure this actually updates properly once we're
    # managing a real plumbing engine and stepping in time.
    @Property(bool, notify=satisfied_changed_signal)
    def satisfied(self):
        return self._condition.satisfied()

    @Property(str, constant=True)
    def condition(self):
        return str(self._condition)

    @Property(str, constant=True)
    def transition(self):
        return str(self._transition)


class ProcedureStepsModel(QAbstractListModel):
    ActionRoleIdx = Qt.UserRole + 1
    OperatorRoleIdx = Qt.UserRole + 2
    ConditionsRoleIdx = Qt.UserRole + 3

    def __init__(self, procedure=None, parent=None):
        QAbstractListModel.__init__(self, parent)
        self.procedure = None
        self.condition_wrappers = None
        self.change_procedure(procedure)

    def change_procedure(self, new_procedure):
        self.layoutAboutToBeChanged.emit()

        self.procedure = new_procedure

        # TODO(jacob): We keep this separate list because we need to be
        # able to notify the Qt engine when a condition ticks from
        # unsatisfied to satisfied or vice-versa. This isn't the
        # cleanest way to do it - is there a better alternative?
        if self.procedure is not None:
            self.condition_wrappers = [
                [ProcedureConditionWrapper(cond, trans, self) for cond, trans in step.conditions]
                for step in self.procedure.step_list
            ]

        self.layoutChanged.emit()

    def refresh(self, step_idx):
        for wrapper in self.condition_wrappers[step_idx]:
            wrapper.satisfied_changed_signal.emit()

    # Qt accessible methods

    def rowCount(self, parent=QModelIndex()):
        if self.procedure is None:
            return 0
        return len(self.procedure.steps)

    def roleNames(self):
        # NOTE(jacob): The values in this dict are byte strings instead
        # of just plain strings because QML expects the return type to
        # be a QHash. Leaving them as plain strings causes a runtime
        # error ('expected hash, got dict'). See below:
        # https://bugreports.qt.io/browse/PYSIDE-703
        return {
            ProcedureStepsModel.ActionRoleIdx: b'action',
            ProcedureStepsModel.OperatorRoleIdx: b'operator',
            ProcedureStepsModel.ConditionsRoleIdx: b'conditions'
        }

    def data(self, index, role):
        if self.procedure is None:
            return None

        try:
            step = self.procedure.step_list[index.row()]
        except IndexError:
            return 'Invalid Index'

        if role == ProcedureStepsModel.ActionRoleIdx:
            action = step.action
            if type(action) == top.StateChangeAction:
                return f'Set {action.component} to {action.state}'
            elif type(action) == top.MiscAction:
                return f'{action.action_type}'
        elif role == ProcedureStepsModel.OperatorRoleIdx:
            return step.operator
        elif role == ProcedureStepsModel.ConditionsRoleIdx:
            return self.condition_wrappers[index.row()]

        return None


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

    def load_from_file(self, filepath):
        with open(filepath) as f:
            proclang = f.read()
        suite = top.proclang.parse(proclang)
        self._proc_eng.load_suite(suite)
        self._refresh_procedure_view()

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
