from PySide2.QtQuick import QQuickPaintedItem
from PySide2.QtGui import QColor, QPen, QFont, QBrush, QImage
from PySide2.QtCore import Qt, Property, Signal, QPointF, Slot, QRectF

import topside as top
from .graphics_node import GraphicsNode
from .graphics_component import GraphicsComponent
from numpy import arctan, cos, sin, round

# Note: Copied from layout_demo to avoid using importlib


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
    A QML-accessible item that will draw the state of the engine.

    It is a subclass of QQuickPaintedItem, which means it imperatively handles all of
    its own events and graphics.
    """

    DEBUG_MODE = False  # Flipping this to True turns on print statements in parts of the code
    # Defines additional (probably temporary) scaling constants
    NODE_RAD = 5

    def __init__(self, parent=None):
        QQuickPaintedItem.__init__(self, parent)

        # Configures item for tracking the mouse and handling mouse events
        self.setAcceptedMouseButtons(Qt.LeftButton | Qt.RightButton)
        self.setAcceptHoverEvents(True)

        # Configures local variables for drawing
        self.engine_instance = None
        self.scaling_factor = 10
        self.scaled = False
        self.color_property = QColor()

        self.upload_engine_instance(make_engine())
        self.graphics_nodes = {}

        self.grid_visible = True
        self.labels_visible = True
        self.components_visible = True
        self.images_visible = True

        self.initial_bounds = None

        self.prepare_drawing_area()

        if self.DEBUG_MODE:
            print('VisualizationArea created!')

    def prepare_drawing_area(self):
        self.resetAllZoomAndPan()
        self.scale_engine_instance()

        t = self.terminal_graph
        pos = self.layout_pos

        for node in t.nodes:
            pt = pos[node]

            self.graphics_nodes[node] = GraphicsNode(pt, self.NODE_RAD, node)

        self.graphics_components = {key: GraphicsComponent(
            key, 'valve') for key in self.engine_instance.component_dict.keys()}

        for comp_key in self.graphics_components.keys():
            for g_node_key in self.graphics_nodes.keys():

                if self.DEBUG_MODE:
                    print(comp_key + ' ' + str(g_node_key))

                if (comp_key + '.') in str(g_node_key):
                    self.graphics_components[comp_key].nodes.append(self.graphics_nodes[g_node_key])

        for comp_key in self.graphics_components.keys():
            comp = self.graphics_components[comp_key]
            comp.calculate_bouding_rect()
            print(comp.name + ": " + str(comp.nodes[0].name) + ' ' + str(comp.nodes[1].name))

    def scale_engine_instance(self):
        t = self.terminal_graph
        pos = self.layout_pos

        for node in t.nodes:
            pt = pos[node]

            if self.DEBUG_MODE:
                print('node: ' + str(pt[0]) + str(pt[1]))

            # Adjusts the coordinates so they fall onto the draw surface
            pt[0] += self.scaling_factor*8
            pt[0] *= self.scaling_factor/2

            pt[1] += self.scaling_factor*2
            pt[1] *= self.scaling_factor/2

            pt[0] = round(pt[0])
            pt[1] = round(pt[1])

            self.graphics_nodes[node] = GraphicsNode(pt, self.NODE_RAD, node)

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

        # Initilizes drawing pens and brushes
        regular_pen = QPen(self.color_property)
        bold_pen = QPen(self.color_property)
        bold_pen.setWidth(bold_pen.width() + 2)
        blue_pen = QPen(Qt.blue)
        red_pen = QPen(Qt.red)
        graph_pen = QPen(Qt.lightGray)

        fill_brush = QBrush()
        fill_brush.setStyle(Qt.SolidPattern)
        fill_brush.setColor(Qt.cyan)

        painter.scale(self.zoom_state, self.zoom_state)
        painter.translate(self.permanent_x_transpose_state + self.temporary_x_transpose_state,
                          self.permanent_y_transpose_state + self.temporary_y_transpose_state)

        if not self.scaled:
            self.initial_bounds = QRectF(painter.viewport())
            self.scaled = True

        painter.setPen(graph_pen)
        painter.drawRect(self.initial_bounds)

        num_horiz_lines = 10
        num_vertical_lines = 10
        vertical_interval = self.initial_bounds.height() / num_vertical_lines
        horiz_interval = self.initial_bounds.width() / num_horiz_lines

        if (self.grid_visible):
            for draw_idx in range(0, 10):
                painter.drawLine(0, draw_idx*vertical_interval,
                                 self.initial_bounds.width(), draw_idx*vertical_interval)
                painter.drawLine(draw_idx*horiz_interval, 0, draw_idx *
                                 horiz_interval, self.initial_bounds.height())

        if self.DEBUG_MODE:
            painter.setFont(big_font)
            painter.drawText(100, 100, 'Display Functional')

        painter.setPen(regular_pen)
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

#                 if not self.scaled:
#                     # Adjusts the coordinates so they fall onto the draw surface
#                     pt[0] += self.scaling_factor*8
#                     pt[0] *= self.scaling_factor/2
#
#                     pt[1] += self.scaling_factor*2
#                     pt[1] *= self.scaling_factor/2
#
#                     pt[0] = round(pt[0])
#                     pt[1] = round(pt[1])
#
#                 if node not in self.graphics_nodes:
#                     self.graphics_nodes[node] = GraphicsNode(pt, NODE_RAD, node)

                painter.drawEllipse(self.graphics_nodes[node])
#                 if self.labels_visible:
#                     painter.setPen(blue_pen)
#                     painter.drawText(pt[0] + 5, pt[1] + 10, str(node))

            for edge in t.edges:
                if pos[edge[0]][0] == pos[edge[1]][0]:
                    if pos[edge[0]][1] < pos[edge[1]][1]:
                        p1 = pos[edge[0]]
                        p2 = pos[edge[1]]
                    else:
                        p1 = pos[edge[1]]
                        p2 = pos[edge[0]]
                elif pos[edge[0]][0] < pos[edge[1]][0]:
                    p1 = pos[edge[0]]
                    p2 = pos[edge[1]]
                else:
                    p1 = pos[edge[1]]
                    p2 = pos[edge[0]]

                # For clipping lines out of nodes
                m_edge = (p2[1] - p1[1])/((p2[0] - p1[0]))
                theta_edge = arctan(m_edge)

                if self.DEBUG_MODE:
                    print('edge1: ' + str(p1[0]) + str(p1[1]))
                    print('edge2: ' + str(p2[0]) + str(p2[1]))

                painter.drawLine(p1[0] + (self.NODE_RAD + 1)*cos(theta_edge),
                                 p1[1] + (self.NODE_RAD + 1)*sin(theta_edge),
                                 p2[0] - (self.NODE_RAD)*cos(theta_edge), p2[1] - (self.NODE_RAD)*sin(theta_edge))

            # Scaling is done on the first draw while nodes are being accessed for the first time
#             if not self.scaled:
#                 self.scaled = True
            if (self.DEBUG_MODE):
                print(list(self.graphics_components.values()))

            if self.components_visible:
                for comp in list(self.graphics_components.values()):
                    painter.drawRect(comp.bounding_rect)

            if self.images_visible:
                for comp in list(self.graphics_components.values()):
                    painter.drawImage(comp.bounding_rect, comp.image)

            if self.labels_visible:
                painter.setPen(red_pen)
                for key, item in self.graphics_nodes.items():
                    painter.drawText(item.center[0] + 5, item.center[1] + 10, str(key))
                painter.setPen(regular_pen)

            if (self.active_node):
                painter.setPen(bold_pen)
                painter.drawEllipse(self.active_node)

                self.requestQMLInfoBox.emit(self.active_node.name, 'valve')
            else:
                self.retractQMLRequest.emit()
#                 painter.fillRect(10,10,50,50, fill_brush)
#
#                 painter.setPen(regular_pen)
#                 painter.drawText(30,30, str(self.active_node.name))
#
#                 painter.setPen(bold_pen)
#                 painter.drawEllipse(self.active_node)

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

        if not self.drag_source:
            self.drag_source = event.pos()
        else:
            self.temporary_x_transpose_state = (event.x() - self.drag_source.x())/self.zoom_state
            self.temporary_y_transpose_state = (event.y() - self.drag_source.y())/self.zoom_state
            self.force_repaint()

        event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_source = None
        self.permanent_x_transpose_state += self.temporary_x_transpose_state
        self.permanent_y_transpose_state += self.temporary_y_transpose_state
        self.temporary_x_transpose_state = 0
        self.temporary_y_transpose_state = 0

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
        self.drag_source = None
        self.permanent_x_transpose_state += self.temporary_x_transpose_state
        self.permanent_y_transpose_state += self.temporary_y_transpose_state
        self.temporary_x_transpose_state = 0
        self.temporary_y_transpose_state = 0

        if self.DEBUG_MODE:
            print('Press: ' + str(event.x()) + ' ' + str(event.y()))

        if event.button() == Qt.RightButton:
            print('right click!')
            self.requestQMLContext.emit()
        else:
            print('left click!')

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

        position_float = QPointF(event.pos())

        position_float.setX(position_float.x()/self.zoom_state
                            - self.permanent_x_transpose_state - self.temporary_x_transpose_state)
        position_float.setY(position_float.y()/self.zoom_state
                            - self.permanent_y_transpose_state - self.temporary_y_transpose_state)

        if self.DEBUG_MODE:
            print('Hover track adjusted: ' + str(position_float.x()) + ' ' + str(position_float.y()))

        for n_key, node in self.graphics_nodes.items():
            if (node.contains(position_float)):
                print('hover detected: ' + str(node.x()) + ' ' + str(node.x()))

                if not self.active_node:
                    self.active_node = node
                    self.force_repaint()

        if self.active_node:
            if not self.active_node.contains(position_float):
                self.active_node = None
                self.force_repaint()

        event.accept()

    def wheelEvent(self, event):
        ZOOM_SENSITIVITY = 0.5

        self.zoom_state += (event.angleDelta().y() / 120)*ZOOM_SENSITIVITY

        if (self.zoom_state <= 0):
            self.zoom_state -= (event.angleDelta().y() / 120)*ZOOM_SENSITIVITY

        print('zoom by ' + str(event.angleDelta().y()) +
              ' and ' + str(event.angleDelta().x()) + ' detected')
        print(str(self.zoom_state))
        self.force_repaint()
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
        self.scaled = False

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

    @Slot(str)
    def log_from_qml(self, text):
        print(text)

    @Slot()
    def force_repaint(self):
        self.update()

    @Slot()
    def print_globals(self):
        print('zoom state: ' + str(self.zoom_state))
        print('permanent x transpose: ' + str(self.permanent_x_transpose_state))
        print('permanent y transpose: ' + str(self.permanent_y_transpose_state))
        print('temporary x transpose: ' + str(self.temporary_x_transpose_state))
        print('temporary y transpose: ' + str(self.temporary_y_transpose_state))
        print('viewport rectangle' + str(self.inital_bounds))

    @Slot(bool)
    def toggleGrid(self, toggle_val):
        self.grid_visible = toggle_val
        self.force_repaint()

    @Slot(bool)
    def toggleComponentVisibility(self, toggle_val):
        self.components_visible = toggle_val
        self.force_repaint()

    @Slot(bool)
    def toggleLabelVisibility(self, toggle_val):
        self.labels_visible = toggle_val
        self.force_repaint()

    @Slot(bool)
    def toggleImageVisibility(self, toggle_val):
        self.images_visible = toggle_val
        self.force_repaint()

    @Slot()
    def resetAllZoomAndPan(self):
        self.active_node = None

        self.drag_source = None

        self.zoom_state = 1

        self.temporary_x_transpose_state = 0
        self.temporary_y_transpose_state = 0
        self.permanent_x_transpose_state = 0
        self.permanent_y_transpose_state = 0

    # Registers color as a QML-accessible property, along with directions for its getter and setter
    color = Property(QColor, get_color, set_color)

    # Registers the signals such that it can be accessible to external QML classesc

    requestQMLContext = Signal(name='requestQMLContext')
    requestQMLInfoBox = Signal(
        str, str, arguments=['node_data', 'comp_data'], name='requestQMLInfoBox')
    retractQMLRequest = Signal(name='retractQMLRequest')
