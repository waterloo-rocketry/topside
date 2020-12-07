import copy

from PySide2.QtCore import QObject, Slot
import numpy as np
from numpy.testing import assert_equal

import topside as top
from ..daq import DAQBridge
from ..plumbing_bridge import PlumbingBridge


class MockPlumbingEngine:
    def __init__(self):
        self.time = 0
        self.pressures = {'n1': 0, 'n2': 0}

    def current_pressures(self):
        return self.pressures

    def step(self, step_size):
        self.time += step_size
        for node in self.pressures:
            self.pressures[node] += 1
        return copy.deepcopy(self.pressures)

    def solve(self, return_resolution):
        states = []
        for i in range(5):
            states.append(self.step(return_resolution))
        return states

    def reset(self):
        self.time = 0
        self.pressures = {node: 0 for node in self.pressures}


class MockPlotter(QObject):
    def __init__(self, daq_bridge):
        QObject.__init__(self)
        self.plot_data = {}
        daq_bridge.dataUpdated.connect(self.updateData)

    @Slot(str, np.ndarray, np.ndarray)
    def updateData(self, channel_name, times, data_vals):
        self.plot_data[channel_name] = (times, data_vals)

    @Slot(str)
    def removeChannel(self, channel_name):
        del self.plot_data[channel_name]


def test_step_forward():
    plumb = PlumbingBridge()
    plumb.step_size = 0.1e6
    plumb.engine = MockPlumbingEngine()
    daq = DAQBridge(plumb)
    plotter = MockPlotter(daq)

    daq.addChannel('n1')
    daq.addChannel('n2')

    plumb.timeStepForward()

    assert_equal(plotter.plot_data, {'n1': ([0.1], [1]),
                                     'n2': ([0.1], [1])})

    plumb.timeStepForward()

    assert_equal(plotter.plot_data, {'n1': ([0.1, 0.2], [1, 2]),
                                     'n2': ([0.1, 0.2], [1, 2])})


def test_track_new_channel():
    plumb = PlumbingBridge()
    plumb.step_size = 0.1e6
    plumb.engine = MockPlumbingEngine()
    daq = DAQBridge(plumb)
    plotter = MockPlotter(daq)

    daq.addChannel('n1')
    plumb.timeStepForward()

    assert_equal(plotter.plot_data, {'n1': ([0.1], [1])})

    daq.addChannel('n2')
    plumb.timeStepForward()

    assert_equal(plotter.plot_data, {'n1': ([0.1, 0.2], [1, 2]),
                                     'n2': ([0.2], [2])})


def test_advance():
    plumb = PlumbingBridge()
    plumb.step_size = 0.1e6
    plumb.engine = MockPlumbingEngine()
    daq = DAQBridge(plumb)
    plotter = MockPlotter(daq)

    daq.addChannel('n1')
    daq.addChannel('n2')

    plumb.timeAdvance()

    times = [0.1, 0.2, 0.3, 0.4, 0.5]
    values = [1, 2, 3, 4, 5]
    assert_equal(plotter.plot_data, {'n1': (times, values),
                                     'n2': (times, values)})


def test_stop():
    plumb = PlumbingBridge()
    plumb.step_size = 0.1e6
    plumb.engine = MockPlumbingEngine()
    daq = DAQBridge(plumb)
    plotter = MockPlotter(daq)

    daq.addChannel('n1')
    daq.addChannel('n2')

    plumb.timeStepForward()
    plumb.timeStepForward()
    plumb.timeStepForward()

    assert_equal(plotter.plot_data, {'n1': ([0.1, 0.2, 0.3], [1, 2, 3]),
                                     'n2': ([0.1, 0.2, 0.3], [1, 2, 3])})

    plumb.timeStop()

    assert_equal(plotter.plot_data, {'n1': ([0], [0]),
                                     'n2': ([0], [0])})


def test_load_engine_resets():
    plumb = PlumbingBridge()
    plumb.step_size = 0.1e6

    e1 = MockPlumbingEngine()
    plumb.load_engine(e1)

    daq = DAQBridge(plumb)
    plotter = MockPlotter(daq)

    daq.channelRemoved.connect(plotter.removeChannel)

    daq.addChannel('n1')
    daq.addChannel('n2')

    plumb.timeStepForward()

    assert_equal(plotter.plot_data, {'n1': ([0.1], [1]),
                                     'n2': ([0.1], [1])})

    plumb.load_engine(e1)

    assert_equal(plotter.plot_data, {})
