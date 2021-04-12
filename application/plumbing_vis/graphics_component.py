from PySide2.QtCore import QRectF, QPointF
from PySide2.QtGui import QImage


class GraphicsComponent():
    """
    A object that acts as the graphical representation of a component.
    """

    def __init__(self, name):
        self.name = name
        self.nodes = []
        self.bounding_rect = None
        self.calculate_bounding_rect()


    def calculate_bounding_rect(self):
        """
        Calculate the bounding rectangle of the component based on what nodes it owns.
        """

        x_sorted = sorted([node.cx for node in self.nodes])
        y_sorted = sorted([node.cy for node in self.nodes])
        x_min = x_sorted[0]
        x_max = x_sorted[-1]
        y_min = y_sorted[0]
        y_max = y_sorted[-1]

        top_left_p = QPointF(x_min - 10, y_min - 10)
        bottom_right_p = QPointF(x_max + 10, y_max + 10)
        self.bounding_rect = QRectF(top_left_p, bottom_right_p)

    def paint(self, painter):
        """
        Handle painting operation delegated from a paint call.
        Note: Currently not used.
        Parameters
        ----------
        painter: QPainter
            The given painter which will execute the graphical commands given to it.
        """

        for node in self.nodes:
            node.paint(painter)
