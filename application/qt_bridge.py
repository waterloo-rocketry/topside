import os
import sys

from PySide2.QtCore import QObject, Slot
from PySide2.QtGui import QGuiApplication, QIcon
from PySide2.QtQml import QQmlApplicationEngine

import operations_simulator as ops


# NOTE(jacob): `__file__` isn't defined for the frozen application,
# so we need to use this function for finding resources in relative
# paths. See below:
# cx-freeze.readthedocs.io/en/latest/faq.html#using-data-files
def find_resource(filename):
    if getattr(sys, 'frozen', False):
        datadir = os.path.dirname(sys.executable)
    else:
        datadir = os.path.dirname(__file__)
    return os.path.join(datadir, 'resources', filename)


class Application:

    def __init__(self, bridge, argv):
        self.bridge = bridge

        self.app = QGuiApplication(argv)
        self.app.setWindowIcon(QIcon(find_resource('icon.ico')))

        self.app.setOrganizationName('Waterloo Rocketry')
        self.app.setOrganizationDomain('waterloorocketry.com')
        self.app.setApplicationName('Operations Simulator')

        self.qml_engine = QQmlApplicationEngine()
        self.qml_engine.load(find_resource('application.qml'))

        self.context = self.qml_engine.rootContext()
        self.context.setContextProperty('context', self.bridge)

    def ready(self):
        return bool(self.qml_engine.rootObjects())

    def run(self):
        return self.app.exec_()


class Bridge(QObject):

    def __init__(self):
        QObject.__init__(self)
        plumb = ops.PlumbingEngine()
