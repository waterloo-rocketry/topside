import os
import sys

from PySide2.QtCore import QUrl
from PySide2.QtQuickWidgets import QQuickWidget


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
    print(path)
    url = QUrl.fromLocalFile(path)
    widget.setSource(url)

    return widget
