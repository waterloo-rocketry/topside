from PySide2.QtCore import QObject, Signal, Slot, QTimer
from PySide2.QtWidgets import QFileDialog
import numpy as np

import topside as top


class PlumbingBridge(QObject):
    engineLoaded = Signal(top.PlumbingEngine)
    dataUpdated = Signal(dict, list)

    def __init__(self):
        QObject.__init__(self)

        self.engine = None
        self.step_size = 0.1e6  # TODO(jacob): Add a UI field for this.
        self.timer = QTimer()
        self.timer.timeout.connect(self.timeStepForward)

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
        self.timer.start(50)

    @Slot()
    def timePause(self):
        self.timer.stop()

    @Slot()
    def timeStop(self):
        self.timer.stop()
        self.engine.reset()
        self.dataUpdated.emit()

    @Slot()
    def timeStepForward(self):
        pressures = self.engine.step(self.step_size)
        self.dataUpdated.emit(pressures, np.array([self.engine.time]))

    @Slot()
    def timeAdvance(self):
        initial_time = self.engine.time
        states = self.engine.solve(return_resolution=self.step_size)

        # TODO(jacob/wendi): Change the data format returned by
        # PlumbingEngine.solve so we don't need to rearrange the data on
        # this side.
        pressures = {node: [] for node in states[0]}
        for state in states:
            for node, pressure in state.items():
                pressures[node].append(pressure)
        pressures_np = {node: np.array(pvals) for node, pvals in pressures.items()}

        times = np.arange(len(states)) * self.step_size + initial_time + self.step_size

        self.dataUpdated.emit(pressures_np, times)
