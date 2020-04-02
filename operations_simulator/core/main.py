import sys

from PySide2.QtWidgets import QApplication, QMainWindow

import operations_simulator as ops


class Window(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("Operations Simulator")


if __name__ == "__main__":
    app = QApplication([])

    plumb = ops.PlumbingEngine()

    window = Window()
    window.resize(1200, 800)
    window.show()

    sys.exit(app.exec_())
