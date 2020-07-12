from PySide2.QtCore import QRectF, QPointF
from PySide2.QtGui import QImage


class GraphicsComponent():
    """
    A object that acts as the graphical representation of a component.

    """

    def __init__(self, name, component_id):
        self.name = name
        self.nodes = []
        self.bounding_rect = None
        self.image = None

        # Loads associated sprite
        self.image = QImage('application/resources/component_icons/' + component_id + '_icon.png')
        if self.image.isNull():
            print('could not load \'' + component_id + '\'!')
        else:
            print('load sucessful!')

    def calculate_bouding_rect(self):
        """
        Calculate the bounding rectangle of the component based on what nodes it owns.

        """
        x_min = x_max = self.nodes[0].center[0]
        y_min = y_max = self.nodes[0].center[1]

        for node in self.nodes[1:]:
            if node.center[0] < x_min:
                x_min = node.center[0]

            if node.center[0] > x_max:
                x_max = node.center[0]

            if node.center[1] < y_min:
                y_min = node.center[1]

            if node.center[1] > y_max:
                y_max = node.center[1]

        top_left_p = QPointF(x_min - 10, y_min - 10)
        bottom_right_p = QPointF(x_max + 10, y_max + 10)
        self.bounding_rect = QRectF(top_left_p, bottom_right_p)

    def pseudo_paint(self, painter):
        """
        Handle painting operation delegated from a paint call.

        Note: Currently not used.

        Parameters
        ----------

        painter: QPainter
            The given painter which will execute the graphical commands given to it.

        """

        pass
