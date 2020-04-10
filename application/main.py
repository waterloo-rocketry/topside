from os import path
import sys

from PySide2.QtWidgets import QMainWindow, QApplication
from PySide2.QtGui import QIcon, QGuiApplication
from PySide2.QtQml import QQmlApplicationEngine

import operations_simulator as ops


# NOTE(jacob): `__file__` isn't defined for the frozen application,
# so we need to use this function for finding resources in relative
# paths. See below:
# cx-freeze.readthedocs.io/en/latest/faq.html#using-data-files
def find_resource(filename):
    if getattr(sys, 'frozen', False):
        datadir = path.dirname(sys.executable)
    else:
        datadir = path.dirname(__file__)
    return path.join(datadir, 'resources', filename)


if __name__ == '__main__':
    app = QGuiApplication(sys.argv)
    app.setWindowIcon(QIcon(find_resource('icon.ico')))

    app.setOrganizationName("Waterloo Rocketry")
    app.setOrganizationDomain("waterloorocketry.com")
    app.setApplicationName("Operations Simulator")

    qml_engine = QQmlApplicationEngine()
    qml_engine.load(find_resource('main_window.qml'))

    plumb = ops.PlumbingEngine()

    if not qml_engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec_())
