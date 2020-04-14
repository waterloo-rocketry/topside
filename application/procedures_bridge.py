from PySide2.QtCore import Qt, Slot, Signal, Property, \
                           QObject, QAbstractListModel, QModelIndex


class ProcedureStepsModel(QAbstractListModel):
    PersonRoleIdx = Qt.UserRole + 1
    StepRoleIdx = Qt.UserRole + 2

    def __init__(self, steps, parent=None):
        QAbstractListModel.__init__(self, parent)
        self.steps = steps
        self.idx = 0

    def rowCount(self, parent=QModelIndex()):
        return len(self.steps)

    def roleNames(self):
        return {
            ProcedureStepsModel.PersonRoleIdx: b'person',
            ProcedureStepsModel.StepRoleIdx: b'step'
        }

    def data(self, index, role):
        if role == ProcedureStepsModel.PersonRoleIdx:
            return 'Primary Technician'
        elif role == ProcedureStepsModel.StepRoleIdx:
            return self.steps[index.row()]
        return None

    def stop(self):
        self.idx = 0

    def previous_step(self):
        if self.idx > 0:
            self.idx -= 1

    def next_step(self):
        if self.idx < self.rowCount() - 1:
            self.idx += 1

    def append_step(self, step):
        row_idx = self.rowCount()
        self.beginInsertRows(QModelIndex(), row_idx, row_idx)
        self.steps.append(step)
        self.endInsertRows()


class ProceduresBridge(QObject):
    goto_step_sig = Signal(int, name='gotoStep')
    steps_changed_sig = Signal(name='stepsChanged')

    def __init__(self):
        QObject.__init__(self)

        self._procedure_steps = ProcedureStepsModel([
            'Open Series Fill Valve',
            'Open Line Vent Valve',
            'Retreat to Mission Control',
            'Open Injector Valve',
        ])

    @Property(QObject, notify=steps_changed_sig)
    def steps(self):
        return self._procedure_steps

    @Slot()
    def play_backwards(self):
        pass

    @Slot()
    def undo(self):
        self._procedure_steps.previous_step()
        self.goto_step_sig.emit(self._procedure_steps.idx)

    @Slot()
    def play(self):
        pass

    @Slot()
    def pause(self):
        pass

    @Slot()
    def stop(self):
        self._procedure_steps.stop()
        self.goto_step_sig.emit(self._procedure_steps.idx)

    @Slot()
    def step_forward(self):
        self._procedure_steps.next_step()
        self.goto_step_sig.emit(self._procedure_steps.idx)

    @Slot()
    def advance(self):
        self._procedure_steps.append_step('Close Injector Valve')
