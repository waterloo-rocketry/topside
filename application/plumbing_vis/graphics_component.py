from PySide2.QtCore import QRectF, QPointF
import numpy as np


class GraphicsComponent():
    """
    A object that acts as the graphical representation of a component.
    """

    def __init__(self, name, nodes, offset=15):
        self.name = name
        self.nodes = nodes
        self.bounding_rect = None
        self.offset = offset

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
        """Paint the nodes of the component"""

        for node in self.nodes:
            node.paint(painter)

    def paint_labels(self, painter, name=True, state=None):
        """
        Paint information associated with the component

        Parameters
        ----------
        name: Bool
            whether to pain the name of the component

        state: str
            Whether to paint the state. To paint the state, pass in the string value for what
            should be painted. If state is a falsy value (eg None, False, "") the state won't be
            printed.
        """
        centroid = self.centroid()
        adjuster = 1

        if name:
            painter.drawText(centroid[0] + self.offset,
                             centroid[1] + adjuster * self.offset, self.name)
            adjuster += 2

        if state:
            painter.drawText(centroid[0] + self.offset,
                             centroid[1] + adjuster * self.offset, state)
            adjuster += 2

    def centroid(self):
        """Return centroid of all nodes of component"""
        return list(np.mean([(node.cx, node.cy) for node in self.nodes], axis=0))

    def __eq__(self, other):
        return type(self) == type(other) and \
            self.name == other.name and \
            sorted(self.nodes) == sorted(other.nodes) and \
            self.offset == other.offset

    def __ne__(self, other):
        return not self.__eq__(other)
