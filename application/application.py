import os
import sys

from PySide2.QtGui import QIcon
from PySide2.QtQml import QQmlApplicationEngine, qmlRegisterType
from PySide2.QtWidgets import QApplication

from .visualization_area import VisualizationArea
from .procedures_bridge import ProceduresBridge
from .plumbing_bridge import PlumbingBridge


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


class Application:

    def __init__(self, argv):
        self.plumbing_bridge = PlumbingBridge()
        self.procedures_bridge = ProceduresBridge(self.plumbing_bridge)

        self.app = QApplication(argv)

        # ALL custom built QQuickItems have to be registered as QML objects in this way:
        qmlRegisterType(VisualizationArea, 'VisualizationArea', 1, 0, 'VisualizationArea')

        self.app.setWindowIcon(QIcon(find_resource('icon.ico')))
        self.app.setOrganizationName('Waterloo Rocketry')
        self.app.setOrganizationDomain('waterloorocketry.com')
        self.app.setApplicationName('Topside')

        self.qml_engine = QQmlApplicationEngine()

        self.context = self.qml_engine.rootContext()
        self.context.setContextProperty('plumbingBridge', self.plumbing_bridge)
        self.context.setContextProperty('proceduresBridge', self.procedures_bridge)

        self.qml_engine.load(find_resource('application.qml'))

        # TODO(jacob): Currently we load these example files at startup
        # to make testing turnaround a bit faster. Figure out how to
        # make the application remember the last file opened, and open
        # that instead.
        self.plumbing_bridge.load_from_files([find_resource('example.pdl')])
        self.procedures_bridge.load_from_file(find_resource('example.proc'))

    def ready(self):
        return len(self.qml_engine.rootObjects()) != 0

    def run(self):
        self.app.aboutToQuit.connect(self.shutdown)
        app_return_code = self.app.exec_()

        return app_return_code

    def shutdown(self):
        # NOTE(jacob): We explicitly `del` this to suppress a TypeError
        # that arises from the Bridge getting destroyed before the
        # engine, causing QML references to go invalid. We attach this
        # cleanup to the aboutToQuit signal because app.exec_ is not
        # guaranteed to return, and therefore placing it immediately
        # after the app.exec_ call would not guarantee that this cleanup
        # routine runs.
        # For reference: https://bugreports.qt.io/browse/QTBUG-81247
        del self.qml_engine
