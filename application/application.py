import os
import sys

from PySide2.QtGui import QGuiApplication, QIcon
from PySide2.QtQml import QQmlApplicationEngine

import operations_simulator as ops
from .procedures_bridge import ProceduresBridge


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
        self.procedures_bridge = ProceduresBridge()

        self.app = QGuiApplication(argv)

        self.app.setWindowIcon(QIcon(find_resource('icon.ico')))
        self.app.setOrganizationName('Waterloo Rocketry')
        self.app.setOrganizationDomain('waterloorocketry.com')
        self.app.setApplicationName('Operations Simulator')

        self.qml_engine = QQmlApplicationEngine()

        self.context = self.qml_engine.rootContext()
        self.context.setContextProperty('proceduresBridge', self.procedures_bridge)

        self.qml_engine.load(find_resource('application.qml'))

    def ready(self):
        return len(self.qml_engine.rootObjects()) != 0

    def run(self):
        app_return_code = self.app.exec_()

        # NOTE(jacob): We explicitly `del` this to suppress a TypeError
        # that arises from the Bridge getting destroyed before the
        # engine, causing QML references to go invalid. This seems to
        # be a Qt bug that arose relatively recently and has not been
        # conclusively resolved: https://forum.qt.io/topic/110356
        del self.qml_engine

        return app_return_code
