from enum import Enum

from PySide2.QtCore import QRectF, QPointF
import numpy as np

class NodeType(Enum):
    PRESSURE_NODE = 1
    COMPONENT_NODE = 2
    ATM_NODE = 3

class GraphicsNode(QRectF):
    """
    A object that acts as the graphical representation of a node.
    Inherits PySide2.QtCore.QRectF.
    """

    def __init__(self, center_point, radius, name, node_type):
        """
        Create a GraphicsNode

        Parameters
        ----------
        center_point: iterable of length 2
            iterable that holds the (x, y) coordinates of the centre point of the node

        radius: int
            radius of node

        name: str
            name of node

        offset: offset at which to print label
        """
        self.name = name
        self.radius = radius
        self.cx = center_point[0]
        self.cy = center_point[1]
        self.node_type = node_type

        top_left = QPointF(self.cx, self.cy)
        bottom_right = QPointF(self.cx, self.cy)

        translation_point = QPointF(radius, radius)

        top_left -= translation_point
        bottom_right += translation_point

        super().__init__(top_left, bottom_right)

    def paint(self, painter):
        painter.drawEllipse(self.center(), self.radius, self.radius)

    def paint_labels(self, painter, offset=None):
        if offset is None:
            offset = 5

        painter.drawText(self.cx + offset, self.cy + offset, self.name)

    def get_centroid(self):
        return np.mean([node.center() for node in self.nodes], axis=0)

    def get_type(self):
        return self.node_type
    
    def set_type(self, node_type):
        self.node_type = node_type

