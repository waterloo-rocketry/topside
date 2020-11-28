import warnings

from PySide2.QtCore import Qt, QObject, Slot, Signal, Property
from PySide2.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QButtonGroup, QCheckBox
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
    dataUpdated = Signal(str, np.ndarray, np.ndarray)  # channel name, time vals, data vals

    def __init__(self, plumbing_bridge):
        QObject.__init__(self)
        plumbing_bridge.dataUpdated.connect(self.update)
        self.data_values = {}
        self.times = np.array([])
        self.window_size_s = 10  # TODO(jacob): Add a UI field for this.

    @Slot(str)
    def addChannel(self, channel_name):
        if channel_name in self.data_values:
            # This should never happen, but we'll put a warning on it
            # just in case.
            warnings.warn('attempted to add a duplicate channel to DAQ')
            return
        self.data_values[channel_name] = np.array([])
        self.channelAdded.emit(channel_name)

    @Slot(str)
    def removeChannel(self, channel_name):
        del self.data_values[channel_name]
        self.channelRemoved.emit(channel_name)

    @Slot(dict, np.ndarray)
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
            channel name and `values` is a NumPy array of new data
            values.

        times: np.ndarray
            `times` is an array of the form `[t1, t2, t3]`. It is
            expected to be the same length as each `values` list. For
            any channel in `datapoints`, `values[i]` is the value of the
            channel at time `times[i]`.
        """
        if len(times) == 0:
            return

        if len(self.times) > 0 and top.micros_to_s(times[0]) < self.times[-1]:
            # We stepped back in time, clear all existing time values.
            # We don't need to clear data_values since they'll
            # automatically be trimmed to the relevant data later on.
            self.times = np.array([])

        trim_time = top.micros_to_s(times[-1]) - self.window_size_s
        appended = np.append(self.times, top.micros_to_s(times))
        self.times = trim_earlier(appended, trim_time)

        for channel, values in datapoints.items():
            if channel in self.data_values:
                extended = np.append(self.data_values[channel], values)

                num_vals = min(len(self.times), len(extended))

                # TODO(jacob): We trim the arrays here to make them the
                # same length, but it could be nicer to front-pad with
                # NaNs so that the time axis is the same across all of
                # the plots. PyQtGraph fixed a bug related to this
                # recently, but the commit hasn't made it into a new
                # release yet.
                self.data_values[channel] = extended[-num_vals:]
                times_to_plot = self.times[-num_vals:]

                self.dataUpdated.emit(channel, times_to_plot, self.data_values[channel])


class DAQLayout(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setLayout(QVBoxLayout())

        self.plot_items = {}  # {channel_name: PlotItem}
        self.plot_curves = {}  # {channel_name: PlotDataItem}
        self.next_row = 0

        self.pen = pg.mkPen(color='g', width=1)

        self.graphs = pg.GraphicsLayoutWidget()
        self.graphs.ci.setBorder('w', width=2)
        self.layout().addWidget(self.graphs)

        self.channel_selector = ChannelSelector()
        self.layout().addWidget(self.channel_selector)

    @Slot(str)
    def addChannel(self, channel_name):
        if channel_name in self.plot_items:
            warnings.warn('attempted to add a duplicate channel to DAQ')
            return
        plot = self.graphs.addPlot(row=self.next_row, col=0, title=channel_name)
        plot.setLimits(minYRange=2)
        plot.showGrid(x=True, y=True)
        self.plot_items[channel_name] = plot
        self.plot_curves[channel_name] = plot.plot(pen=self.pen)

        # NOTE(jacob): PyQtGraph doesn't adjust row numbers if an item
        # is deleted from the layout, so we can't simply assume that the
        # next row available is (number of plots + 1). Fortunately,
        # the actual values of the assigned row numbers don't seem to
        # matter, so we just need to make sure the "next row" is higher
        # than all of the others so far.
        self.next_row += 1

    @Slot(str)
    def removeChannel(self, channel_name):
        item = self.plot_items[channel_name]

        # NOTE(jacob): For some reason, PyQtGraph doesn't properly
        # delete the border geometry for plot items when removeItem is
        # called on a GraphicsLayout (or GraphicsLayoutWidget), so we
        # need to explicitly delete it ourselves or we get weird lines
        # left on the screen. I'm considering submitting a PR to fix
        # this, if I can confirm that it's actually a bug.
        border = self.graphs.ci.itemBorders[item]
        self.graphs.ci.scene().removeItem(border)

        self.graphs.removeItem(item)
        item.deleteLater()

        del self.plot_items[channel_name]
        del self.plot_curves[channel_name]

    @Slot(str, np.ndarray, np.ndarray)
    def updateData(self, channel_name, times, data_vals):
        curve = self.plot_curves[channel_name]
        curve.setData(times, data_vals)


class ChannelSelector(QWidget):
    channelSelected = Signal(str)
    channelDeselected = Signal(str)

    def __init__(self):
        QWidget.__init__(self)
        self.setLayout(QGridLayout())

        self.control_group = QButtonGroup()
        self.control_group.setExclusive(False)
        self.control_group.idToggled.connect(self.notifyChannel)
        self.ids_to_channels = {}  # {id: channel_name (str)}
        self.checkboxes = {}  # {channel_name: QCheckBox}

        self.next_id = 0

        # TODO(jacob): 4 columns is mostly an arbitrary choice; 5 seemed
        # too crowded, 3 seemed too empty. Ideally we'd change this
        # dynamically based on the column width.
        self.num_cols = 4

    def add_checkbox(self, channel_name):
        if channel_name in self.checkboxes:
            warnings.warn('attempted to add a duplicate checkbox to the DAQ channel selector')
            return
        checkbox = QCheckBox(channel_name)
        self.checkboxes[channel_name] = checkbox

        num_widgets = len(self.checkboxes)
        row = (num_widgets - 1) // self.num_cols
        col = (num_widgets - 1) % self.num_cols
        self.layout().addWidget(checkbox, row, col)

        self.control_group.addButton(checkbox, self.next_id)
        self.ids_to_channels[self.next_id] = channel_name
        self.next_id += 1

    def clear_checkboxes(self):
        for checkbox in self.checkboxes.values():
            self.control_group.removeButton(checkbox)
            self.layout().removeWidget(checkbox)
            checkbox.deleteLater()
        self.checkboxes = {}
        self.ids_to_channels = {}

    @Slot(top.PlumbingEngine)
    def updateNodeList(self, plumb):
        self.clear_checkboxes()
        for node in plumb.nodes(data=False):
            self.add_checkbox(node)

    @Slot(int)
    def notifyChannel(self, checkbox_id, is_checked):
        channel = self.ids_to_channels[checkbox_id]
        if is_checked:
            self.channelSelected.emit(channel)
        else:
            self.channelDeselected.emit(channel)


def make_daq_widget(daq_bridge, plumbing_bridge):
    layout = DAQLayout()

    daq_bridge.channelAdded.connect(layout.addChannel)
    daq_bridge.channelRemoved.connect(layout.removeChannel)
    daq_bridge.dataUpdated.connect(layout.updateData)

    layout.channel_selector.channelSelected.connect(daq_bridge.addChannel)
    layout.channel_selector.channelDeselected.connect(daq_bridge.removeChannel)

    plumbing_bridge.engineLoaded.connect(layout.channel_selector.updateNodeList)

    return layout
