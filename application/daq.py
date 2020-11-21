import warnings

from PySide2.QtCore import Qt, QObject, Slot, Signal, Property
import pyqtgraph as pg
import numpy as np

import topside as top


def trim_earlier(array, t):
    """
    Return the portion of an array falling after a reference value.

    Parameters
    ----------

    array: list or numpy.ndarray
        The array to trim. Must be monotonically increasing.

    t: number
        The reference value used for trimming the array.

    Returns an array corresponding to the portion of `array` after the
    first value greater than or equal to `t`.

    For example:
        trim_earlier([1, 3, 5], 2) == [3, 5]
        trim_earlier([4, 6, 8], 6) == [6, 8]
        trim_earlier([10, 20, 30], 40) == []
    """
    i = 0
    while i < len(array) and array[i] < t:
        i += 1
    return array[i:]


class DAQBridge(QObject):
    channelAdded = Signal(str)
    channelRemoved = Signal(str)
    dataUpdated = Signal(str, list, list)  # channel name, time vals, data vals

    def __init__(self, plumbing_bridge):
        QObject.__init__(self)
        plumbing_bridge.dataUpdated.connect(self.update)
        self.data_values = {}
        self.times = np.array([])
        self.window_size_s = 10  # TODO(jacob): Add a UI field for this.

    @Slot(str)
    def addChannel(self, channel_name):
        if channel_name in self.data_values:
            warnings.warn('attempted to add a duplicate channel to DAQ')
            return
        self.data_values[channel_name] = np.array([])
        self.channelAdded.emit(channel_name)

    @Slot(str)
    def removeChannel(self, channel_name):
        del self.data_values[channel_name]
        self.channelRemoved.emit(channel_name)

    @Slot(dict, list)
    def update(self, datapoints, times):
        """
        Update the tracked data channels with new data.

        This function will automatically trim the existing data to
        remain within the window size. For example, if the window size
        is 10s, we have data from 12s to 22s, and we get new data from
        22s to 25s, we will end up with data from 15s to 25s after
        calling `update`.

        Parameters
        ----------

        datapoints: dict
            `datapoints` is a dict of the form `{channel: values}`,
            where `channel` is a string corresponding to a tracked
            channel name and `values` is a list of new data values.

        times: list
            `times` is a list of the form `[t1, t2, t3]`. It is expected
            to be the same length as each `values` list. For any channel
            in `datapoints`, `values[i]` is the value of the channel at
            time `times[i]`.
        """
        if len(times) == 0:
            return

        trim_time = top.micros_to_s(times[-1]) - self.window_size_s
        appended = np.append(self.times, top.micros_to_s(times))
        self.times = trim_earlier(appended, trim_time)

        for channel, values in datapoints.items():
            if channel in self.data_values:
                extended = np.append(self.data_values[channel], values)
                self.data_values[channel] = extended[-len(self.times):]
                self.dataUpdated.emit(channel, self.times, self.data_values[channel])


class DAQPlotWidget(pg.GraphicsLayoutWidget):
    def __init__(self, parent=None):
        pg.GraphicsLayoutWidget.__init__(self, parent)
        self.plots = {}
        self.rows = {}

    @Slot(str)
    def addChannel(self, channel_name):
        if channel_name in self.plots:
            warnings.warn('attempted to add a duplicate channel to DAQ')
            return
        new_row_num = len(self.rows)
        plot = self.addPlot(row=new_row_num, col=0)
        plot.setLimits(minYRange=1)
        self.plots[channel_name] = plot.plot()
        self.rows[channel_name] = new_row_num

    @Slot(str)
    def removeChannel(self, channel_name):
        self.removeItem(self.rows[channel_name], 0)
        del self.plots[channel_name]
        del self.rows[channel_name]

    @Slot(str, list, list)
    def updateData(self, channel_name, times, data_vals):
        plot = self.plots[channel_name]
        plot.setData(times, data_vals)
