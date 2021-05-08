from PySide2.QtQuick import QQuickPaintedItem
from PySide2.QtGui import QColor, QPen, QFont
from PySide2.QtCore import Qt, Property, Slot

import topside as top
from .graphics_node import GraphicsNode, NodeType
from .graphics_component import GraphicsComponent


def get_positioning_params(coords, canvas_width, canvas_height, fill_percentage=1.0):
    """
    Determine the scale and offset required to center coordinates in a box.

    The returned parameters will always ensure that the coordinates are
    within the limits of the box and that aspect ratio is preserved.

    Parameters
    ----------

    coords: iterable
        Each value in coords is a tuple (x, y) representing a point from
        the original set of coordinates that require adjustment. The
        original iterable will not be modified.

    canvas_width: float
    canvas_height: float
        The dimensions of the canvas that the coordinates will be
        positioned on.

    fill_percentage: float [default=1.0]
        If set to a value less than 1.0, the coordinates will only fill
        a percentage of the canvas. For example, a canvas height of 10
        and fill percentage of 0.8 will scale the y-values from 1 to 9;
        this range (8) covers 80% of the canvas height and still
        centers the coordinates in the overall canvas.

    Returns
    -------

    scale: float
    x_offset: float
    y_offset: float

        In order to position the points appropriately, apply the
        following transformation:

        (x, y) -> ((scale * x) + x_offset, (scale * y) + y_offset)
    """
    if fill_percentage <= 0:
        raise ValueError(f"fill percentage must be >0, got {fill_percentage}")
    elif fill_percentage > 1:
        raise ValueError(f"fill percentage must be <=1, got {fill_percentage}")

    width = canvas_width * fill_percentage
    height = canvas_height * fill_percentage

    x_vals = []
    y_vals = []
    for x_val, y_val in coords:
        x_vals.append(x_val)
        y_vals.append(y_val)

    x_min = min(x_vals)
    x_max = max(x_vals)
    y_min = min(y_vals)
    y_max = max(y_vals)

    dx = x_max - x_min
    dy = y_max - y_min

    if dx > 0 and dy > 0:
        scale = min(width / dx, height / dy)
    else:
        scale = 1

    x_center = (x_min + x_max) / 2
    y_center = (y_min + y_max) / 2

    x_offset = (canvas_width / 2) - x_center * scale
    y_offset = (canvas_height / 2) - y_center * scale

    return scale, x_offset, y_offset


class VisualizationArea(QQuickPaintedItem):
    """
    A QML-accessible item that will draw the state of the engine.

    It is a subclass of QQuickPaintedItem, which means it imperatively handles all of
    its own events and graphics.
    """

    DEBUG_MODE = False  # Flipping this to True turns on print statements in parts of the code

    def __init__(self, parent=None):
        QQuickPaintedItem.__init__(self, parent)

        # Configures item for tracking the mouse and handling mouse events
        self.setAcceptedMouseButtons(Qt.LeftButton)
        self.setAcceptHoverEvents(True)

        # Configures local variables for drawing
        self.engine_instance = None
        self.terminal_graph = None
        self.layout_pos = None
        self.graphics_nodes = {}
        self.graphics_components = {}
        self.components = {}
        self.scaling_factor = 0.8
        self.scaled = False
        self.color_property = QColor()

        self.big_font = QFont('Times', 25, QFont.Bold)
        self.small_font = QFont('Arial', 7)

        self.node_font = QFont('Arial', 8)
        self.component_font = QFont('Arial', 8, QFont.Bold)

        self.heightChanged.connect(self.setRescaleNeeded)
        self.widthChanged.connect(self.setRescaleNeeded)

        if self.DEBUG_MODE:
            print('VisualizationArea created!')

    def scale_and_center(self):
        """
        Scale coordinates to fill and center in the visualization pane.
        """
        scale, x_offset, y_offset = get_positioning_params(self.layout_pos.values(), self.width(),
                                                           self.height(), self.scaling_factor)

        for node in self.terminal_graph.nodes:
            self.layout_pos[node][0] *= scale
            self.layout_pos[node][0] += x_offset
            self.layout_pos[node][1] *= scale
            self.layout_pos[node][1] += y_offset

    def paint(self, painter):
        """
        Detail the instruction for how the item is to be rendered in the application.

        Overloads the paint method from `QQuickItem`.

        Parameters
        ----------

        painter: QPainter
            The painter instance which will draw all of the primitives.
        """
        # Sets painter to use local color
        pen = QPen(self.color_property)
        painter.setPen(pen)

        if self.DEBUG_MODE:
            painter.setFont(self.big_font)
            painter.drawText(100, 100, 'Display Functional')

        if self.engine_instance:
            if self.DEBUG_MODE:
                print('engine print active')

            # Scaling is done on the first draw while nodes are being accessed for the first time
            if not self.scaled:
                self.scale_and_center()
                self.scaled = True

            # create GraphicsNodes for each node
            self.create_graphics()

            # paint nodes
            self.paint_nodes(painter)

            # paint edges
            self.paint_edges(painter)

            # paint components
            for cname in self.components.keys():
                self.paint_component(painter, cname, name=True, state=True)

            if self.DEBUG_MODE:
                print('engine print complete')

    def create_graphics(self):
        t = self.terminal_graph
        pos = self.layout_pos

        # create GraphicsNodes for each node
        self.graphics_nodes = {node: GraphicsNode(
            (pos[node][0], pos[node][1]), 5, node, NodeType.COMPONENT_NODE) for node in t.nodes}

        # Set pressure node types
        for orig_node in self.engine_instance.nodes(data=False):
            if orig_node in self.graphics_nodes:
                self.graphics_nodes[orig_node].set_type(NodeType.PRESSURE_NODE)

        # create GraphicsComponent for each component
        self.graphics_components = {}
        for component_name, node_names in self.components.items():
            nodes = [self.graphics_nodes[node] for node in node_names]
            self.graphics_components[component_name] = GraphicsComponent(component_name, nodes)

    def paint_edges(self, painter):
        """Paint the edges of the engine"""
        for edge in self.terminal_graph.edges:
            p1 = self.layout_pos[edge[0]]
            p2 = self.layout_pos[edge[1]]

            if self.DEBUG_MODE:
                print('edge1: ' + str(p1[0]) + str(p1[1]))
                print('edge2: ' + str(p2[0]) + str(p2[1]))

            painter.drawLine(p1[0], p1[1], p2[0], p2[1])

    def paint_component(self, painter, component, name=True, state=False):
        """Paint a component on the graph"""
        original_pen = painter.pen()

        painter.setFont(self.component_font)

        state_name = None
        if state:
            state_name = self.engine_instance.current_state(component)

        graphics_component = self.graphics_components[component]

        pen = QPen(QColor(0, 0, 255))
        painter.setPen(pen)
        graphics_component.paint(painter)

        painter.setPen(original_pen)
        graphics_component.paint_labels(painter, name, state_name)

    def paint_nodes(self, painter):
        """Paint the pressure nodes of the engine, not including the subnodes of a component"""
        painter.setFont(self.node_font)
        for node in self.graphics_nodes.values():
            if self.DEBUG_MODE:
                print('node: ' + node.cx + node.cy)

            node.paint(painter)
            if node.get_type() == NodeType.PRESSURE_NODE:
                node.paint_labels(painter)

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

    @Slot(top.PlumbingEngine)
    def uploadEngineInstance(self, engine):
        """
        Set the local engine to the input variable and initialize associated local objects.

        Setter and initializer for uploading an engine to be displayed. After an engine is set,
        the according layout and terminal graph is generated from the engine data.

        Parameters
        ----------

        engine: topside.plumbing_engine
            An instance of the topside engine to be displayed.
        """

        self.engine_instance = engine
        self.terminal_graph = top.terminal_graph(self.engine_instance)
        self.components = top.component_nodes(self.engine_instance)
        self.layout_pos = top.layout_plumbing_engine(self.engine_instance)
        self.create_graphics()
        self.setRescaleNeeded()
        self.update()

    @Slot()
    def setRescaleNeeded(self):
        self.scaled = False

    # Registers color as a QML-accessible property, along with directions for its getter and setter
    color = Property(QColor, get_color, set_color)
