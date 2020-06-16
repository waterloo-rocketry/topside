from PySide2.QtQuick import QQuickPaintedItem
from PySide2.QtGui import QColor, QPen, QPainter, QFont
from PySide2.QtCore import Qt, Property, QPointF 

import importlib.util
import topside as top


class VisualizationArea(QQuickPaintedItem):
    """
    A QML-acessible item that will draw the state of the engine. It is a subclass of 
    QQuickPaintedItem, which means it imperatively handles all of it's own events and graphics. 
    """
    
    DEBUG_MODE = False #: Flipping this to positive turns on print statments in parts of the code
    
    def __init__(self, parent = None):
        # Temporary spec import of the make_engine() function for testing
        spec = importlib.util.spec_from_file_location('layout_demo.name', \
                'C:/Users/Artem Sotnikov/Desktop/design teams/' + \
                'topside/topside/visualization/tests/layout_demo.py')
        
        layout_demo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(layout_demo)
            
        QQuickPaintedItem.__init__(self, parent)
        
        # Configures item for tracking the mouse and handling mouse events
        self.setAcceptedMouseButtons(Qt.LeftButton)
        self.setAcceptHoverEvents(True)
        
        # Configures local variables for drawing
        self.engine_instance = None
        self.scaling_factor = 10            
        self.scaled = False                
        self._color = QColor()
        
        # Creates instance of test engine
        self.upload_engine_instance(layout_demo.make_engine())
        
        if (self.DEBUG_MODE):        
            print('VisualizationArea created!')
        
    
    def paint(self, painter):
        """
        Overloads the paint method from `QQuickItem`

        Details the instruction for how the item is to be rendered in the application

        Parameters
        ----------

        painter: QPainter
            The painter instance which will draw all of the primitives
        
        """
        # Creates fonts
        big_font = QFont('Times', 25, QFont.Bold)
        smol_font = QFont('Arial', 7)
        
        # Sets painter to use local color
        pen = QPen(self._color)
        painter.setPen(pen)
                
        if (self.DEBUG_MODE):
            painter.setFont(big_font)
            painter.drawText(100,100, 'Display Functional');
            
        painter.setFont(smol_font) # Sets font
        
        if (self.engine_instance):
            if (self.DEBUG_MODE):
                print('engine print active')
            
            # Uses the drawing algorithm from plotting.py to draw the graph using the painter
                        
            t = self.terminal_graph 
            pos = self.layout_pos
            
            for node in t.nodes:
                pt = pos[node]
                
                if (self.DEBUG_MODE):
                    print('node: ' + str(pt[0]) + str(pt[1]))
                    
                if (not self.scaled): 
                    # Adjusts the coordinates so they fall onto the draw surface
                    pt[0] += self.scaling_factor*8
                    pt[0] *= self.scaling_factor/2
                    
                    pt[1] += self.scaling_factor*2
                    pt[1] *= self.scaling_factor/2
                                    
                
                painter.drawEllipse(QPointF(pt[0],pt[1]),5,5)
                painter.drawText(pt[0]+ 5, pt[1]+ 10, str(node)) 
        
            for edge in t.edges:
                p1 = pos[edge[0]]                
                p2 = pos[edge[1]]
                
                if (self.DEBUG_MODE):
                    print('edge1: ' + str(p1[0]) + str(p1[1]))
                    print('edge2: ' + str(p2[0]) + str(p2[1]))
                
                painter.drawLine(p1[0], p1[1], p2[0], p2[1])
            
            if (not self.scaled):
                self.scaled = True
            
            if (self.DEBUG_MODE):
                print('engine print complete')
            
        
    def mouseMoveEvent(self, event):
        """
        Overloads the mouseMoveEvent method from `QQuickItem`

        Is called whenever a mouse move (or drag) is registered on the draw surface

        Parameters
        ----------

        event: QMouseEvent 
            The event which contains all of the data about where the move occured        
        """
        
        if (self.DEBUG_MODE):
            print('Drag Track:' + str(event.x()) + ' ' + str(event.y()))
        event.accept()
        
    def mousePressEvent(self, event):
        """
        Overloads the mousePressEvent method from `QQuickItem`

        Is called whenever a mouse press is registered on the draw surface

        Parameters
        ----------

        event: QMouseEvent 
            The event which contains all of the data about where the press occured        
        """
        if (self.DEBUG_MODE):
            print('Press: ' + str(event.x()) + ' ' + str(event.y()))        
        event.accept()
        
    def hoverMoveEvent(self, event):
        """
        Overloads the hoverMoveEvent method from `QQuickItem`

        Is called whenever a hover move (or mouse move without being pressed) is registered on the 
        draw surface

        Parameters
        ----------

        event: QHoverEvent 
            The event which contains all of the data about where the hover move occurred        
        """
        if (self.DEBUG_MODE):
            print ('Hover track: ' + str(event.pos().x()) + ' ' + str(event.pos().y()))
        event.accept()
        
    def upload_engine_instance(self, engine):
        """
        Setter and initializer for uploading an engine to be displayed. After an engine is set,
        the according layout and terminal graph is generated from the engine data 

        Parameters
        ----------

        engine: topside.plumbing_engine 
            An instance of the topside engine to be displayed     
        """
        
        self.engine_instance = engine
        self.terminal_graph = top.terminal_graph(self.engine_instance)
        self.layout_pos = top.layout_plumbing_engine(self.engine_instance)
        
    def getColor(self):
        """
        Getter for the qml-acessible color property 'color', which is registered by
        a 'Property' call at the end of the file

        Returns
        ----------

        QColor: 
            The local graphics QColor    
        """
        return self._color
    
    def setColor(self, input):
        """
        Setter for the qml-acessible color property 'color', which is registered by
        a 'Property' call at the end of the file

        Returns
        ----------

        input: QColor 
            The local graphics QColor    
        """
        self._color = input
        
    # Registers color as a qml-acessible property, along with directions for its getter and setter        
    color = Property(QColor, getColor, setColor) 
    test = Property(int)
    
    
