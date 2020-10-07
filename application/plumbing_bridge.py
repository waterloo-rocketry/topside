from PySide2.QtCore import QObject, Signal, Slot
from PySide2.QtWidgets import QFileDialog

import topside as top


class PlumbingBridge(QObject):
    engineLoaded = Signal(top.PlumbingEngine)

    def __init__(self):
        QObject.__init__(self)

        self.engine = None

    def load_engine(self, new_engine):
        self.engine = new_engine
        self.engineLoaded.emit(new_engine)

    def load_from_file(self, filepath):
        parser = top.pdl.Parser([filepath])
        new_engine = parser.make_engine()

        self.load_engine(new_engine)

    @Slot()
    def loadFromDialog(self):
        # TODO(jacob): Make this menu remember the last file opened
        filepath, _ = QFileDialog.getOpenFileName(self.parent(), 'Load PDL file')
        if filepath != '':
            self.load_from_file(filepath)
