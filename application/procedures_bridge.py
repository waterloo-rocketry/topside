from PySide2.QtCore import Qt, Slot, Signal, Property, \
    QObject, QAbstractListModel, QModelIndex
from PySide2.QtWidgets import QFileDialog

import topside as top


# TODO(jacob): Delete this test code and load a real engine

class MockPlumbingEngine:
    def __init__(self):
        pass

    def step(self, dt):
        pass

    def set_component_state(self, component, state):
        pass

    def current_pressures(self):
        return {}


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
        self.procedure = procedure

    def change_procedure(self, new_procedure):
        self.layoutAboutToBeChanged.emit()
        self.procedure = new_procedure
        self.layoutChanged.emit()

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
            return [ProcedureConditionWrapper(cond, trans, self) for cond, trans in step.conditions]

        return None


class ProceduresBridge(QObject):
    goto_step_sig = Signal(int, name='gotoStep')
    steps_changed_sig = Signal(name='dataChanged')

    def __init__(self):
        QObject.__init__(self)

        plumb = MockPlumbingEngine()

        self._procedures_engine = top.ProceduresEngine(plumb)
        self._procedure_steps = ProcedureStepsModel()
        self._refresh_procedure_view()

    def _refresh_procedure_view(self):
        proc = self._procedures_engine.current_procedure()
        displayed_proc = self._procedure_steps.procedure

        if proc is None:
            self._procedure_steps.change_procedure(None)
            return

        if displayed_proc is None or displayed_proc.procedure_id != proc.procedure_id:
            self._procedure_steps.change_procedure(proc)

        idx = proc.index_of(self._procedures_engine.current_step.step_id)
        self.goto_step_sig.emit(idx)

    @Property(QObject, notify=steps_changed_sig)
    def steps(self):
        return self._procedure_steps

    @Slot()
    def loadProcedureSuite(self):
        # TODO(jacob): Make this menu remember the last file opened
        filepath, _ = QFileDialog.getOpenFileName(self.parent(), 'Load ProcLang file')
        if filepath != '':
            with open(filepath) as f:
                proclang = f.read()
            suite = top.proclang.parse(proclang)
            self._procedures_engine.load_suite(suite)
            self._refresh_procedure_view()

    @Slot()
    def playBackwards(self):
        pass

    @Slot()
    def undo(self):
        pass

    @Slot()
    def play(self):
        pass

    @Slot()
    def pause(self):
        pass

    @Slot()
    def stop(self):
        # TODO(jacob): Should this reset the plumbing engine as well?
        self._procedures_engine.reset()
        self._refresh_procedure_view()

    @Slot()
    def stepForward(self):
        self._procedures_engine.next_step()
        self._refresh_procedure_view()

    @Slot()
    def advance(self):
        pass
