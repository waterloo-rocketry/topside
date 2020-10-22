from PySide2.QtCore import Qt, QObject, Slot, Signal, Property, QAbstractListModel, QModelIndex

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

    def __eq__(self, other):
        return type(self) == type(other) and \
            self._condition == other._condition and \
            self._transition == other._transition


class ProcedureStepsModel(QAbstractListModel):
    ActionRoleIdx = Qt.UserRole + 1
    OperatorRoleIdx = Qt.UserRole + 2
    ConditionsRoleIdx = Qt.UserRole + 3

    def __init__(self, procedure=None, parent=None):
        QAbstractListModel.__init__(self, parent)
        self.procedure = None
        self.condition_wrappers = []
        self.change_procedure(procedure)

    def change_procedure(self, new_procedure):
        self.layoutAboutToBeChanged.emit()

        self.procedure = new_procedure

        # TODO(jacob): We keep this separate list because we need to be
        # able to notify the Qt engine when a condition ticks from
        # unsatisfied to satisfied or vice-versa. This isn't the
        # cleanest way to do it - is there a better alternative?
        if self.procedure is None:
            self.condition_wrappers = []
        else:
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
