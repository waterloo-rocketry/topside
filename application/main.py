from os import path
import sys

from PySide2.QtWidgets import QApplication, QMainWindow
from PySide2.QtGui import QIcon

import operations_simulator as ops


# NOTE(jacob): `__file__` isn't defined for the frozen application,
# so we need to use this function for finding resources in relative
# paths. See below:
# cx-freeze.readthedocs.io/en/latest/faq.html#using-data-files
def find_resource(filename):
    if getattr(sys, 'frozen'):
        datadir = path.dirname(sys.executable)
    else:
        datadir = path.dirname(__file__)
    return path.join(datadir, 'resources', filename)


class Window(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle('Operations Simulator')
        self.setWindowIcon(QIcon(find_resource('icon.ico')))


if __name__ == '__main__':
    app = QApplication([])

    plumb = ops.PlumbingEngine()

    window = Window()
    window.resize(1200, 800)
    window.show()

    sys.exit(app.exec_())
