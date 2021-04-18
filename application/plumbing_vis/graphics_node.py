from enum import Enum

from PySide2.QtCore import QRectF, QPointF


class NodeType(Enum):
    PRESSURE_NODE = 1
    COMPONENT_NODE = 2
    ATM_NODE = 3


class GraphicsNode(QRectF):
    """
    A object that acts as the graphical representation of a node.
    Inherits PySide2.QtCore.QRectF.
    """

    def __init__(self, center_point, radius, name, node_type=NodeType.PRESSURE_NODE):
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

        node_type: NodeType
            enum that specifies the type of node, eg engine pressure node or component subnode

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
        """Paint an ellipse for the location of the node"""
        painter.drawEllipse(self.center(), self.radius, self.radius)

    def paint_labels(self, painter, offset=None):
        """Paint the node name"""
        if offset is None:
            offset = 5

        painter.drawText(self.cx + offset, self.cy + offset, self.name)

    def get_type(self):
        return self.node_type

    def set_type(self, node_type):
        self.node_type = node_type

    def __eq__(self, other):
        return type(self) == type(other) and \
            self.name == other.name and \
            self.radius == other.radius and \
            self.center() == other.center() and\
            self.node_type == other.node_type

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return self.name < other.name

    def __gt__(self, other):
        return self.name > other.name
