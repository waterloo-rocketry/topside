import os
import sys

from PySide2.QtCore import Qt, QUrl, QTimer
from PySide2.QtGui import QIcon, QKeySequence
from PySide2.QtQml import QQmlEngine, qmlRegisterType
from PySide2.QtWidgets import QApplication, QMainWindow, QSplitter, QMenu, QAction
from PySide2.QtQuickWidgets import QQuickWidget

from .visualization_area import VisualizationArea
from .procedures_bridge import ProceduresBridge
from .plumbing_bridge import PlumbingBridge
from .daq import DAQBridge, make_daq_widget


# NOTE(jacob): `__file__` isn't defined for the frozen application,
# so we need to use this function for finding resources in relative
# paths. See below:
# https://cx-freeze.readthedocs.io/en/latest/faq.html#using-data-files
def find_resource(filename):
    if getattr(sys, 'frozen', False):
        datadir = os.path.dirname(sys.executable)
    else:
        datadir = os.path.dirname(__file__)
    return os.path.join(datadir, 'resources', filename)


def make_qml_widget(engine, qml_file):
    widget = QQuickWidget(engine, None)
    widget.setResizeMode(QQuickWidget.SizeRootObjectToView)

    path = find_resource(qml_file)
    widget.setSource(QUrl.fromLocalFile(path))

    return widget


class Application:
    def __init__(self, argv):
        self.plumbing_bridge = PlumbingBridge()
        self.procedures_bridge = ProceduresBridge(self.plumbing_bridge)
        self.daq_bridge = DAQBridge(self.plumbing_bridge)

        self.app = QApplication(argv)

        # ALL custom built QQuickItems have to be registered as QML objects in this way:
        qmlRegisterType(VisualizationArea, 'VisualizationArea', 1, 0, 'VisualizationArea')

        self.app.setWindowIcon(QIcon(find_resource('icon.ico')))
        self.app.setOrganizationName('Waterloo Rocketry')
        self.app.setOrganizationDomain('waterloorocketry.com')
        self.app.setApplicationName('Topside')

        self.qml_engine = QQmlEngine()
        context = self.qml_engine.rootContext()
        context.setContextProperty('plumbingBridge', self.plumbing_bridge)
        context.setContextProperty('proceduresBridge', self.procedures_bridge)

        self.main_window = self._make_main_window()

        # TODO(jacob): Currently we load these example files at startup
        # to make testing turnaround a bit faster. Figure out how to
        # make the application remember the last file opened, and open
        # that instead.
        self.plumbing_bridge.load_from_files([find_resource('example.pdl')])
        self.procedures_bridge.load_from_file(find_resource('example.proc'))

    def _make_main_window(self):
        # TODO(jacob): Should we move this code somewhere else (maybe
        # into a separate MainWindow class)?
        window = QMainWindow()

        vert_splitter = QSplitter(Qt.Vertical)
        vert_splitter.setChildrenCollapsible(False)

        horiz_splitter = QSplitter(Qt.Horizontal)
        horiz_splitter.setChildrenCollapsible(False)

        daq_widget = make_daq_widget(self.daq_bridge, self.plumbing_bridge)
        horiz_splitter.addWidget(daq_widget)

        plumb_widget = make_qml_widget(self.qml_engine, 'PlumbingPane.qml')
        plumb_widget.setMinimumWidth(600)
        plumb_widget.setMinimumHeight(600)
        horiz_splitter.addWidget(plumb_widget)

        proc_widget = make_qml_widget(self.qml_engine, 'ProceduresPane.qml')
        proc_widget.setMinimumWidth(400)
        proc_widget.setMinimumHeight(600)
        horiz_splitter.addWidget(proc_widget)

        vert_splitter.addWidget(horiz_splitter)

        controls_widget = make_qml_widget(self.qml_engine, 'ControlsPane.qml')
        controls_widget.setMinimumHeight(200)

        vert_splitter.addWidget(controls_widget)

        window.setCentralWidget(vert_splitter)

        file_menu = QMenu('&File')

        open_proc_action = QAction('Open Procedure Suite', window)
        open_proc_action.setShortcut(QKeySequence('Ctrl+O'))
        open_proc_action.triggered.connect(self.procedures_bridge.loadFromDialog)
        file_menu.addAction(open_proc_action)

        open_plumb_action = QAction('Open Plumbing Engine', window)
        open_plumb_action.setShortcut(QKeySequence('Ctrl+Shift+O'))
        open_plumb_action.triggered.connect(self.plumbing_bridge.loadFromDialog)
        file_menu.addAction(open_plumb_action)

        exit_action = QAction('Exit', window)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(window.close)
        file_menu.addAction(exit_action)

        window.menuBar().addMenu(file_menu)

        return window

    def run(self):
        self.app.aboutToQuit.connect(self.shutdown)

        self.main_window.showMaximized()
        app_return_code = self.app.exec_()

        return app_return_code

    def shutdown(self):
        # NOTE(jacob): We explicitly `del` this to suppress a TypeError
        # that arises from the bridges getting destroyed before the QML
        # engine, causing QML references to go invalid. We attach this
        # cleanup to the aboutToQuit signal because app.exec_ is not
        # guaranteed to return, and therefore placing it immediately
        # after the app.exec_ call would not guarantee that this cleanup
        # routine runs.
        # For reference: https://bugreports.qt.io/browse/QTBUG-81247
        del self.qml_engine
