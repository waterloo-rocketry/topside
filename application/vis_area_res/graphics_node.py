from PySide2.QtCore import QRectF, QPointF


class GraphicsNode(QRectF):

    def __init__(self, center_point, radius, name):
        self.name = name
        self.center = center_point

        top_left = QPointF(center_point[0], center_point[1])
        bottom_right = QPointF(center_point[0], center_point[1])

        translation_point = QPointF(radius, radius)

        top_left -= translation_point
        bottom_right += translation_point

        super().__init__(top_left, bottom_right)
