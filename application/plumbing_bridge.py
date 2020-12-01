from PySide2.QtCore import QObject, Signal, Slot
from PySide2.QtWidgets import QFileDialog

import topside as top


class PlumbingBridge(QObject):
    engineLoaded = Signal(top.PlumbingEngine)
    dataUpdated = Signal()

    def __init__(self):
        QObject.__init__(self)

        self.engine = None

    def load_engine(self, new_engine):
        self.engine = new_engine
        self.engineLoaded.emit(new_engine)

    def load_from_files(self, filepaths):
        parser = top.pdl.Parser(filepaths)
        new_engine = parser.make_engine()

        self.load_engine(new_engine)

    @Slot()
    def loadFromDialog(self):
        # TODO(jacob): Make this menu remember the last file opened
        filepaths, _ = QFileDialog.getOpenFileNames(self.parent(), 'Load PDL files')
        if len(filepaths) > 0:
            self.load_from_files(filepaths)

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
        self.engine.reset()
        self.dataUpdated.emit()

    @Slot()
    def timeStepForward(self):
        step_size = 0.1e6  # TODO(jacob): Add a UI field for this.
        self.engine.step(step_size)
        self.dataUpdated.emit()

    @Slot()
    def timeAdvance(self):
        self.engine.solve()
        self.dataUpdated.emit()
