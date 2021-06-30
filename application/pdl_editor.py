from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import QWidget, QMainWindow, QSplitter, QVBoxLayout, QGridLayout, \
    QPlainTextEdit, QPushButton
from PySide2.QtGui import QFont

import topside as top
from .plumbing_vis.visualization_area import WidgetVisualizationArea


class PDLEditor(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setLayout(QGridLayout())

        split = QSplitter(Qt.Horizontal)
        split.setChildrenCollapsible(False)

        self.vis_area = WidgetVisualizationArea()
        split.addWidget(self.vis_area)

        edit_pane = QWidget()
        edit_pane.setLayout(QVBoxLayout())

        font = QFont('Courier New', 11)

        self.editor = QPlainTextEdit()
        self.editor.document().setDefaultFont(font)
        edit_pane.layout().addWidget(self.editor)

        compile_b = QPushButton("Compile")
        compile_b.clicked.connect(self.compilePDL)
        edit_pane.layout().addWidget(compile_b)

        self.messages = QPlainTextEdit()
        self.messages.setReadOnly(True)
        self.messages.document().setDefaultFont(font)
        edit_pane.layout().addWidget(self.messages)

        split.addWidget(edit_pane)

        self.layout().addWidget(split)

    @Slot()
    def compilePDL(self):
        self.messages.appendPlainText('------------')

        pdl_text = self.editor.toPlainText()

        try:
            parser = top.Parser([pdl_text], 's')
            plumb = parser.make_engine()
        except Exception as e:
            self.messages.appendPlainText('Error encountered in PDL compilation:')
            self.messages.appendPlainText(str(e))
            scrollbar = self.messages.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
            return

        if not plumb.is_valid():
            self.messages.appendPlainText('Plumbing engine is invalid:')
            error_str = str('\n'.join([e.error_message for e in plumb.error_set]))
            self.messages.appendPlainText(error_str)
            scrollbar = self.messages.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
            return

        self.messages.appendPlainText('PDL compilation successful')
        scrollbar = self.messages.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

        self.vis_area.visualizer.uploadEngineInstance(plumb)


def make_pdl_editor(parent):
    pdl_editor = PDLEditor()

    w = QMainWindow(parent=parent)
    w.setCentralWidget(pdl_editor)
    w.setWindowModality(Qt.WindowModal)

    w.resize(1000, 800)

    return w
