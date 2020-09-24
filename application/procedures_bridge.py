from PySide2.QtCore import Qt, Slot, Signal, Property, \
    QObject, QAbstractListModel, QModelIndex

import topside as top


# TODO(jacob): Delete this test code and load a real engine and procedure

class MockPlumbingEngine:
    def __init__(self):
        pass

    def step(self, dt):
        pass

    def set_component_state(self, component, state):
        pass

    def current_pressures(self):
        return {}


def build_test_procedure_suite():
    open_action_1 = top.StateChangeAction('c1', 'open')
    open_action_2 = top.StateChangeAction('c2', 'open')
    close_action_1 = top.StateChangeAction('c1', 'closed')
    close_action_2 = top.StateChangeAction('c2', 'closed')

    # Add miscellaneous action
    misc_action = top.MiscAction('Approach the tower')

    s1 = top.ProcedureStep('s1', open_action_1, [(top.Immediate(), top.Transition('p1', 's2'))])
    s2 = top.ProcedureStep('s2', open_action_2, [(top.Immediate(), top.Transition('p1', 's5'))])

    # The step contain misc action
    s5 = top.ProcedureStep('s5', misc_action, [(top.Immediate(), top.Transition('p2', 's3'))])

    p1 = top.Procedure('p1', [s1, s2, s5])

    s3 = top.ProcedureStep('s3', close_action_1, [(top.Immediate(), top.Transition('p2', 's4'))])
    s4 = top.ProcedureStep('s4', close_action_2, [(top.Immediate(), top.Transition('p1', 's1'))])

    p2 = top.Procedure('p2', [s3, s4])

    return top.ProcedureSuite([p1, p2], 'p1')


class ProcedureStepsModel(QAbstractListModel):
    PersonRoleIdx = Qt.UserRole + 1
    StepRoleIdx = Qt.UserRole + 2

    def __init__(self, procedure, parent=None):
        QAbstractListModel.__init__(self, parent)
        self.procedure = procedure

    def change_procedure(self, new_procedure):
        self.layoutAboutToBeChanged.emit()
        self.procedure = new_procedure
        self.layoutChanged.emit()

    # Qt accessible methods

    def rowCount(self, parent=QModelIndex()):
        return len(self.procedure.steps)

    def roleNames(self):
        # NOTE(jacob): The values in this dict are byte strings instead
        # of just plain strings because QML expects the return type to
        # be a QHash. Leaving them as plain strings causes a runtime
        # error ('expected hash, got dict'). See below:
        # https://bugreports.qt.io/browse/PYSIDE-703
        return {
            ProcedureStepsModel.PersonRoleIdx: b'person',
            ProcedureStepsModel.StepRoleIdx: b'step'
        }

    def data(self, index, role):
        try:
            step = self.procedure.step_list[index.row()]
        except IndexError:
            return 'Invalid Index'
        if role == ProcedureStepsModel.PersonRoleIdx:
            return 'Primary Technician'
        elif role == ProcedureStepsModel.StepRoleIdx:
            action = step.action 
            # Check if misc action or not
            if type(action) == top.StateChangeAction : 
                return f'Set {action.component} to {action.state}'
            elif type(action) == top.MiscAction :
                return f'{action.action_Type}'
        return None


class ProceduresBridge(QObject):
    goto_step_sig = Signal(int, name='gotoStep')
    steps_changed_sig = Signal(name='dataChanged')

    def __init__(self):
        QObject.__init__(self)

        plumb = MockPlumbingEngine()
        suite = build_test_procedure_suite()

        self._procedures_engine = top.ProceduresEngine(plumb, suite)
        self._procedure_steps = ProcedureStepsModel(self._procedures_engine.current_procedure())

    def _refresh_procedure_view(self):
        proc = self._procedures_engine.current_procedure()

        if self._procedure_steps.procedure.procedure_id != proc.procedure_id:
            self._procedure_steps.change_procedure(proc)

        idx = proc.index_of(self._procedures_engine.current_step.step_id)
        self.goto_step_sig.emit(idx)

    @Property(QObject, notify=steps_changed_sig)
    def steps(self):
        return self._procedure_steps

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
        pass

    @Slot()
    def stepForward(self):
        self._procedures_engine.next_step()
        self._refresh_procedure_view()

    @Slot()
    def advance(self):
        pass