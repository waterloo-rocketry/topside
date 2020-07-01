from PySide2.QtQuick import QQuickPaintedItem
from PySide2.QtGui import QColor, QPen, QFont
from PySide2.QtCore import Qt, Property, QPointF

import topside as top

# NOTE: Copied from layout_demo to avoid using importlib
def make_engine():
    states = {
        'static': {
            (1, 2, 'A1'): 1,
            (2, 1, 'A2'): 1
        }
    }
    edges = [(1, 2, 'A1'), (2, 1, 'A2')]

    mapping = {'c1': {1: 'atm', 2: 1},
               'c2': {1: 1, 2: 2},
               'c3': {1: 1, 2: 2},
               'c4': {1: 2, 2: 3},
               'c5': {1: 3, 2: 'atm'},
               'c6': {1: 3, 2: 4},
               'c7': {1: 4, 2: 5},
               'c8': {1: 4, 2: 5},
               'c9': {1: 5, 2: 6},
               'c10': {1: 6, 2: 'atm'},
               'c11': {1: 6, 2: 'atm'},
               'c12': {1: 6, 2: 'atm'}}

    pressures = {}
    for k1, v1 in mapping.items():
        for k2, v2 in v1.items():
            pressures[v2] = (0, False)

    component_dict = {k: top.PlumbingComponent(k, states, edges) for k in mapping.keys()}
    initial_states = {k: 'static' for k in mapping.keys()}

    return top.PlumbingEngine(component_dict, mapping, pressures, initial_states)


class VisualizationArea(QQuickPaintedItem):
    """
    A QML-acessible item that will draw the state of the engine.

    It is a subclass of QQuickPaintedItem, which means it imperatively handles all of
    its own events and graphics.
    """

    DEBUG_MODE = False  # Flipping this to True turns on print statments in parts of the code

    def __init__(self, parent=None):
        QQuickPaintedItem.__init__(self, parent)

        # Configures item for tracking the mouse and handling mouse events
        self.setAcceptedMouseButtons(Qt.LeftButton)
        self.setAcceptHoverEvents(True)

        # Configures local variables for drawing
        self.engine_instance = None
        self.scaling_factor = 10
        self.scaled = False
        self.color_property = QColor()

        self.upload_engine_instance(make_engine())

        if self.DEBUG_MODE:
            print('VisualizationArea created!')

    def paint(self, painter):
        """
        Detail the instruction for how the item is to be rendered in the application.

        Overloads the paint method from `QQuickItem`.

        Parameters
        ----------

        painter: QPainter
            The painter instance which will draw all of the primitives.
        """
        # Creates fonts
        big_font = QFont('Times', 25, QFont.Bold)
        small_font = QFont('Arial', 7)

        # Sets painter to use local color
        pen = QPen(self.color_property)
        painter.setPen(pen)

        if self.DEBUG_MODE:
            painter.setFont(big_font)
            painter.drawText(100, 100, 'Display Functional')

        painter.setFont(small_font)  # Sets font

        if self.engine_instance:
            if self.DEBUG_MODE:
                print('engine print active')

            # Uses the drawing algorithm from plotting.py to draw the graph using the painter

            t = self.terminal_graph
            pos = self.layout_pos

            for node in t.nodes:
                pt = pos[node]

                if self.DEBUG_MODE:
                    print('node: ' + str(pt[0]) + str(pt[1]))

                if not self.scaled:
                    # Adjusts the coordinates so they fall onto the draw surface
                    pt[0] += self.scaling_factor*8
                    pt[0] *= self.scaling_factor/2

                    pt[1] += self.scaling_factor*2
                    pt[1] *= self.scaling_factor/2

                painter.drawEllipse(QPointF(pt[0], pt[1]), 5, 5)
                painter.drawText(pt[0] + 5, pt[1] + 10, str(node))

            for edge in t.edges:
                p1 = pos[edge[0]]
                p2 = pos[edge[1]]

                if self.DEBUG_MODE:
                    print('edge1: ' + str(p1[0]) + str(p1[1]))
                    print('edge2: ' + str(p2[0]) + str(p2[1]))

                painter.drawLine(p1[0], p1[1], p2[0], p2[1])

            # Scaling is done on the first draw while nodes are being accessed for the first time
            if not self.scaled:
                self.scaled = True

            if self.DEBUG_MODE:
                print('engine print complete')

    def mouseMoveEvent(self, event):
        """
        Handle the mouse event for a mouse dragging action.

        Is called automatically by the object whenever a mouse move (or drag) is registered on the
        draw surface. Overloads the mouseMoveEvent method from `QQuickItem`.

        Parameters
        ----------

        event: QMouseEvent
            The event which contains all of the data about where the move occurred.
        """

        if self.DEBUG_MODE:
            print('Drag Track:' + str(event.x()) + ' ' + str(event.y()))
        event.accept()

    def mousePressEvent(self, event):
        """
        Handle the mouse event for a mouse press action.

        Is called automatically by the object whenever a mouse move (or drag) is registered on the
        draw surface. Overloads the mouseMoveEvent method from `QQuickItem`.

        Parameters
        ----------

        event: QMouseEvent
            The event which contains all of the data about where the press occurred.
        """
        if self.DEBUG_MODE:
            print('Press: ' + str(event.x()) + ' ' + str(event.y()))
        event.accept()

    def hoverMoveEvent(self, event):
        """
        Handle the mouse event for a mouse hover move action.

        Is called automatically by the object whenever the mouse is moved without anything being
        pressed down (i.e. the mouse is being hovered). Overloads the hoverMoveEvent method from
        `QQuickItem`.

        Parameters
        ----------

        event: QHoverEvent
            The event which contains all of the data about where the hover move occurred.
        """
        if self.DEBUG_MODE:
            print('Hover track: ' + str(event.pos().x()) + ' ' + str(event.pos().y()))
        event.accept()

    def upload_engine_instance(self, engine):
        """
        Sets the local engine to the input variable and initializes associated local objects.

        Setter and initializer for uploading an engine to be displayed. After an engine is set,
        the according layout and terminal graph is generated from the engine data.

        Parameters
        ----------

        engine: topside.plumbing_engine
            An instance of the topside engine to be displayed.
        """

        self.engine_instance = engine
        self.terminal_graph = top.terminal_graph(self.engine_instance)
        self.layout_pos = top.layout_plumbing_engine(self.engine_instance)

    def get_color(self):
        """
        Return the local color.

        Getter for the QML-accessible color property 'color', which is registered by
        a 'Property' call at the end of the file.

        Returns
        -------

        QColor:
            The local graphics QColor.
        """
        return self.color_property

    def set_color(self, input_color):
        """
        Set the local color to the given color.

        Setter for the QML-accessible color property 'color', which is registered by
        a 'Property' call at the end of the file.

        Parameters
        ----------

        input: QColor
            The local graphics QColor.
        """
        self.color_property = input_color

    # Registers color as a QML-acessible property, along with directions for its getter and setter
    color = Property(QColor, get_color, set_color)
