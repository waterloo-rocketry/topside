import copy

from numpy.testing import assert_equal

import topside as top
from ..daq import DAQBridge
from ..plumbing_bridge import PlumbingBridge


class MockPlumbingEngine:
    def __init__(self):
        self.time = 0
        self.pressures = {'n1': 0, 'n2': 0}

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


def test_step_forward():
    plumb = PlumbingBridge()
    plumb.engine = MockPlumbingEngine()
    daq = DAQBridge(plumb)
    daq.addChannel('n1')
    daq.addChannel('n2')

    plumb.timeStepForward()

    assert_equal(daq.times, [0.1])
    assert_equal(daq.data_values, {'n1': [1], 'n2': [1]})

    plumb.timeStepForward()

    assert_equal(daq.times, [0.1, 0.2])
    assert_equal(daq.data_values, {'n1': [1, 2], 'n2': [1, 2]})


def test_advance():
    plumb = PlumbingBridge()
    plumb.engine = MockPlumbingEngine()
    daq = DAQBridge(plumb)
    daq.addChannel('n1')
    daq.addChannel('n2')

    plumb.timeAdvance()

    assert_equal(daq.times, [0.1, 0.2, 0.3, 0.4, 0.5])
    assert_equal(daq.data_values, {'n1': [1, 2, 3, 4, 5], 'n2': [1, 2, 3, 4, 5]})
