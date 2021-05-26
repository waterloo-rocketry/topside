import textwrap

import pytest

import topside as top
from ..visualization_area import get_positioning_params, PlumbingVisualizer, QMLVisualizationArea
from ..graphics_node import GraphicsNode, NodeType
from ..graphics_component import GraphicsComponent
from .testing_utils import MockLine, MockPainter


COMPONENT_NAME = 'injector_valve'


def make_plumbing_engine():
    pdl = textwrap.dedent(f"""\
    name: example

    body:
    - component:
        name: {COMPONENT_NAME}
        edges:
          edge1:
              nodes: [A, B]
        states:
          open:
              edge1: 1
          closed:
              edge1: closed
    - graph:
        name: main
        nodes:
          A:
            initial_pressure: 100
            components:
              - [{COMPONENT_NAME}, A]
          B:
            initial_pressure: 0
            components:
              - [{COMPONENT_NAME}, B]
        states:
          {COMPONENT_NAME}: closed
    """)
    parser = top.Parser(pdl, 's')
    return parser.make_engine()


def test_get_positioning_params_one_val():
    coords = [(10, 20)]

    w = 10
    h = 10

    scale, x_offset, y_offset = get_positioning_params(coords, w, h)

    assert scale == 1
    assert x_offset == -5
    assert y_offset == -15


def test_get_positioning_params_scale_to_height():
    coords = [(0, 0), (8, 5)]

    w = 20
    h = 10

    scale, x_offset, y_offset = get_positioning_params(coords, w, h)

    assert scale == 2
    assert x_offset == 2
    assert y_offset == 0


def test_get_positioning_params_scale_to_width():
    coords = [(1, 1), (9, 7)]

    w = 24
    h = 30

    scale, x_offset, y_offset = get_positioning_params(coords, w, h)

    assert scale == 3
    assert x_offset == -3
    assert y_offset == 3


def test_get_positioning_params_fill_percentage_height():
    coords = [(0, 0), (6, 5)]

    w = 32
    h = 20
    fp = 0.75  # gives w = 24, h = 15

    scale, x_offset, y_offset = get_positioning_params(coords, w, h, fp)

    assert scale == 3
    assert x_offset == 7
    assert y_offset == 2.5


def test_get_positioning_params_fill_percentage_width():
    coords = [(0, 0), (3, 4)]

    w = 10
    h = 20
    fp = 0.9  # gives w = 9, h = 18

    scale, x_offset, y_offset = get_positioning_params(coords, w, h, fp)

    assert scale == 3
    assert x_offset == 0.5
    assert y_offset == 4


def test_bad_fill_percentages():
    coords = [(0, 0), (6, 5)]

    w = 32
    h = 20

    with pytest.raises(Exception):
        get_positioning_params(coords, w, h, 0)
    with pytest.raises(Exception):
        get_positioning_params(coords, w, h, 10)


def test_vis_area_scale_and_center():
    va = QMLVisualizationArea()

    va.setWidth(30)
    va.setHeight(20)

    va.visualizer.terminal_graph = top.terminal_graph(make_plumbing_engine())
    va.visualizer.layout_pos = {'A': [0, 0], f'{COMPONENT_NAME}.A': [1, 1],
                                'B': [3, 2], f'{COMPONENT_NAME}.B': [2, 1]}

    va.visualizer.scale_and_center()

    # 80% box of the 30x20 rectangle gives [xmin, xmax] = [3, 27] and
    # [ymin, ymax] = [2, 18].
    assert va.visualizer.layout_pos == {'A': [3, 2], f'{COMPONENT_NAME}.A': [11, 10],
                                        'B': [27, 18], f'{COMPONENT_NAME}.B': [19, 10]}


def make_vis_area():
    va = QMLVisualizationArea()

    va.setWidth(30)
    va.setHeight(20)

    plumb = make_plumbing_engine()

    # Assign these directly because we want to use a hardcoded layout,
    # not the automatic layout that uploadEngineInstance would trigger.
    va.visualizer.engine_instance = plumb
    va.visualizer.terminal_graph = top.terminal_graph(plumb)
    va.visualizer.components = top.component_nodes(plumb)
    va.visualizer.layout_pos = {'A': [0, 0], f'{COMPONENT_NAME}.A': [1, 1],
                                'B': [3, 2], f'{COMPONENT_NAME}.B': [2, 1]}

    return va


def test_vis_area_node_paint():
    va = make_vis_area()

    painter = MockPainter()
    va.paint(painter)

    r = 5  # ellipse radius (will be the same for x and y)
    expected_ellipses = [(3, 2, r, r), (11, 10, r, r), (27, 18, r, r), (19, 10, r, r)]

    for expected in expected_ellipses:
        assert expected in painter.ellipses

    expected_lines = [MockLine((3, 2), (11, 10)), MockLine((11, 10), (19, 10)),
                      MockLine((19, 10), (27, 18))]

    for expected in expected_lines:
        assert expected in painter.lines

    offset = 5
    expected_texts = [(3 + offset, 2 + offset, 'A'),
                      (27 + offset, 18 + offset, 'B')]

    for expected in expected_texts:
        assert expected in painter.texts


def test_vis_area_component_paint():
    va = make_vis_area()
    va.visualizer.terminal_graph = top.terminal_graph(make_plumbing_engine())
    va.visualizer.layout_pos = {'A': [0, 0], f'{COMPONENT_NAME}.A': [1, 1],
                                'B': [3, 2], f'{COMPONENT_NAME}.B': [2, 1]}
    va.visualizer.create_graphics()

    painter = MockPainter()
    r = 5

    va.visualizer.paint_component(painter, COMPONENT_NAME, name=False)
    expected_ellipses = [(1, 1, r, r), (2, 1, r, r)]
    assert expected_ellipses == painter.ellipses
    painter.clear()

    va.visualizer.paint_component(painter, COMPONENT_NAME, state=True)
    centroid = va.visualizer.graphics_components[COMPONENT_NAME].centroid()
    offset = va.visualizer.graphics_components[COMPONENT_NAME].offset
    state = 'closed'
    expected_text = [
        (centroid[0] + offset, centroid[1] + offset, COMPONENT_NAME),
        (centroid[0] + offset, centroid[1] + 3*offset, state)
    ]
    assert expected_text == expected_text


def test_create_components():
    va = make_vis_area()
    va.visualizer.terminal_graph = top.terminal_graph(make_plumbing_engine())
    va.visualizer.layout_pos = {'A': [0, 0], f'{COMPONENT_NAME}.A': [1, 1],
                                'B': [3, 2], f'{COMPONENT_NAME}.B': [2, 1]}
    va.visualizer.create_graphics()

    component_nodeA = GraphicsNode((1, 1), 5, 'injector_valve.A', NodeType.COMPONENT_NODE)
    component_nodeB = GraphicsNode((2, 1), 5, 'injector_valve.B', NodeType.COMPONENT_NODE)

    expected_nodes = {
        'A': GraphicsNode((0, 0), 5, 'A'),
        'B': GraphicsNode((3, 2), 5, 'B'),
        'injector_valve.A': component_nodeA,
        'injector_valve.B': component_nodeB
    }
    expected_components = {
        COMPONENT_NAME: GraphicsComponent(COMPONENT_NAME, [component_nodeA, component_nodeB])
    }

    assert va.visualizer.graphics_nodes == expected_nodes
    assert va.visualizer.graphics_components == expected_components
