from PySide2.QtCore import Qt, QObject, Signal, Slot, Property, QTimer
from PySide2.QtWidgets import QFileDialog
import numpy as np

import topside as top


class PlumbingBridge(QObject):
    engineLoaded = Signal(top.PlumbingEngine)
    dataUpdated = Signal(dict, np.ndarray)
    pausedChanged = Signal()

    def __init__(self):
        QObject.__init__(self)

        self.engine = None
        self.step_size = 0.05e6  # TODO(jacob): Add a UI field for this.
        self.timer = QTimer()
        self.timer.setTimerType(Qt.PreciseTimer)
        self.timer.timeout.connect(self.step_time)
        self._paused = True

    def load_engine(self, new_engine):
        self.engine = new_engine
        self.engineLoaded.emit(new_engine)

    def load_from_files(self, filepaths):
        parser = top.pdl.Parser(filepaths)
        new_engine = parser.make_engine()

        self.load_engine(new_engine)

    def step_time(self):
        pressures = self.engine.step(self.step_size)
        self.dataUpdated.emit(pressures, np.array([self.engine.time]))

    def set_paused(self, should_pause):
        if should_pause:
            self.timer.stop()
        self._paused = should_pause
        self.pausedChanged.emit()

    def get_paused(self):
        return self._paused

    # `paused` is both a Python property and a Qt property, which means
    # we can directly treat it as a variable. Writing `paused = True`
    # will call set_paused(True).
    paused = Property(bool, get_paused, set_paused, notify=pausedChanged)

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
        self.paused = False
        self.timer.start(50)

    @Slot()
    def timePause(self):
        self.paused = True

    @Slot()
    def timeStop(self):
        self.paused = True
        self.engine.reset()
        self.dataUpdated.emit(self.engine.current_pressures(), np.array([self.engine.time]))

    @Slot()
    def timeStepForward(self):
        self.paused = True
        self.step_time()

    @Slot()
    def timeAdvance(self):
        self.paused = True
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
