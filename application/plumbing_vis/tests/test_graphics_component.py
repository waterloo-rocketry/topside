from PySide2.QtCore import QRectF, QPointF

from ..graphics_component import GraphicsComponent
from ..graphics_node import GraphicsNode

from .testing_utils import MockLine, MockPainter


def create_component():
    nodes = [GraphicsNode((0, 1), 5, 'node1'), GraphicsNode(
        (1, 2), 5, 'node2'), GraphicsNode((5, 0), 5, 'node3')]
    return GraphicsComponent('component', nodes)


def test_get_centroid():
    component = create_component()

    expected = [(0 + 1 + 5)/3, (1 + 2 + 0)/3]
    assert component.centroid() == expected


def test_calculate_bounding_rect():
    component = create_component()

    top_left = QPointF(0 - 10, 0 - 10)
    bottom_right = QPointF(5 + 10, 2 + 10)

    expected = QRectF(top_left, bottom_right)
    component.calculate_bounding_rect()

    assert component.bounding_rect == expected


def test_component_paint():
    painter = MockPainter()
    component = create_component()

    component.paint(painter)

    r = 5
    expected_ellipses = [
        (0, 1, r, r),
        (1, 2, r, r),
        (5, 0, r, r)
    ]

    assert expected_ellipses == painter.ellipses


def test_component_labels():
    painter = MockPainter()
    component = create_component()

    # no name, no state
    component.paint_labels(painter, name=False)
    expected_text = []
    assert painter.texts == expected_text
    painter.clear()

    centroid = component.centroid()
    offset = component.offset

    # only name
    component.paint_labels(painter)
    expected_text = [(centroid[0] + offset, centroid[1] + offset, 'component')]
    assert painter.texts == expected_text
    painter.clear()

    # only state
    state = 'state'
    component.paint_labels(painter, name=False, state=state)
    expected_text = [(centroid[0] + offset, centroid[1] + offset, state)]
    assert painter.texts == expected_text
    painter.clear()

    # both
    component.paint_labels(painter, name=True, state=state)
    expected_text = [
        (centroid[0] + offset, centroid[1] + offset, 'component'),
        (centroid[0] + offset, centroid[1] + 3*offset, state)
    ]
    assert painter.texts == expected_text
    painter.clear()


def test_comparisons():
    component = create_component()

    equals = create_component()
    not_equals = create_component()
    not_equals.name = 'NOTEQUAL'

    assert component == equals
    assert component != not_equals
