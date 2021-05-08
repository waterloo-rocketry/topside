from .testing_utils import MockPainter
from ..graphics_node import GraphicsNode, NodeType


def test_paint():
    painter = MockPainter()
    node = GraphicsNode((1, 1), 5, 'node')

    node.paint(painter)

    r = 5
    expected = [(1, 1, r, r)]

    assert painter.ellipses == expected


def test_paint_labels():
    painter = MockPainter()
    name = 'node'
    node = GraphicsNode((1, 1), 5, name)

    node.paint_labels(painter)

    # default offset
    expected = [(1 + 5, 1 + 5, name)]
    assert painter.texts == expected
    painter.clear()

    # specified offset
    node.paint_labels(painter, offset=0)
    expected = [(1, 1, name)]
    assert painter.texts == expected


def test_type():
    node = GraphicsNode((1, 1), 5, 'node')

    assert node.get_type() == NodeType.PRESSURE_NODE

    node.set_type(NodeType.COMPONENT_NODE)
    assert node.get_type() == NodeType.COMPONENT_NODE


def test_comparisons():
    node1 = GraphicsNode((1, 1), 5, 'node')

    equals = GraphicsNode((1, 1), 5, 'node')
    less = GraphicsNode((1, 1), 5, 'a')
    greater = GraphicsNode((1, 1), 5, 'z')

    assert node1 == equals
    assert node1 != less
    assert less < node1
    assert greater > node1
