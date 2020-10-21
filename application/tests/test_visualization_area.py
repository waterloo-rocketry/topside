import textwrap
from dataclasses import dataclass

import pytest

import topside as top
from ..visualization_area import get_positioning_params, VisualizationArea


@dataclass
class MockLine:
    """
    Helper class for testing line drawing.

    We don't care if a line is drawn from A->B or B->A and we want the
    two cases to be considered equal, so we define this class and
    override the __eq__ and __hash__ methods.
    """
    p1: tuple
    p2: tuple

    def __eq__(self, other):
        return (type(self) == type(other)) and \
               ((self.p1 == other.p1 and self.p2 == other.p2) or \
                (self.p1 == other.p2 and self.p2 == other.p1))

    def __lt__(self, other):
        """
        Returns True if self < other, and False otherwise.

        We define this so that we can sort lists with MockLines in them.
        We want ordering to be the same if p1 and p2 are swapped, so we
        sort the points before comparing.
        """
        return sorted([self.p1, self.p2]) < sorted([other.p1, other.p2])


def test_mock_line():
    """Sanity check test to make sure that MockLine works"""
    l1 = MockLine((1, 2), (3, 4))
    l2 = MockLine((3, 4), (1, 2))
    l3 = MockLine((1, 2), (4, 5))
    l4 = MockLine((1, 2), (0, 10))

    assert l1 == l2
    assert not l1 < l2
    assert not l2 < l1

    assert l1 != l3
    assert l1 < l3

    assert l1 != l4
    assert l4 < l1


class MockPainter:
    """
    Helper class for testing visualization area painting.

    We pass an instance of this class into the `paint` method. Instead
    of actually drawing something on the screen, this class just keeps
    track of all of the primitives that it's been instructed to render.
    """

    def __init__(self):
        self.ellipses = []
        self.lines = []
        self.texts = []

    def setPen(self, pen):
        pass

    def setFont(self, font):
        pass

    def drawEllipse(self, center, rx, ry):
        self.ellipses.append((center.x(), center.y(), rx, ry))

    def drawLine(self, x1, y1, x2, y2):
        self.lines.append(MockLine((x1, y1), (x2, y2)))

    def drawText(self, x, y, text):
        self.texts.append((x, y, text))


def make_plumbing_engine():
    pdl = textwrap.dedent("""\
    name: example

    body:
    - component:
        name: injector_valve
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
              - [injector_valve, A]
          B:
            initial_pressure: 0
            components:
              - [injector_valve, B]
        states:
          injector_valve: closed
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
    va = VisualizationArea()

    va.setWidth(30)
    va.setHeight(20)

    va.terminal_graph = top.terminal_graph(make_plumbing_engine())
    va.layout_pos = {'A': [0, 0], 'injector_valve.A': [1, 1],
                     'B': [3, 2], 'injector_valve.B': [2, 1]}

    va.scale_and_center()

    # 80% box of the 30x20 rectangle gives [xmin, xmax] = [3, 27] and
    # [ymin, ymax] = [2, 18].
    assert va.layout_pos == {'A': [3, 2], 'injector_valve.A': [11, 10],
                             'B': [27, 18], 'injector_valve.B': [19, 10]}


def test_vis_area_paint():
    va = VisualizationArea()

    va.setWidth(30)
    va.setHeight(20)

    plumb = make_plumbing_engine()

    # Assign these directly because we want to use a hardcoded layout,
    # not the automatic layout that uploadEngineInstance would trigger.
    va.engine_instance = plumb
    va.terminal_graph = top.terminal_graph(plumb)
    va.layout_pos = {'A': [0, 0], 'injector_valve.A': [1, 1],
                     'B': [3, 2], 'injector_valve.B': [2, 1]}

    painter = MockPainter()
    va.paint(painter)

    r = 5  # ellipse radius (will be the same for x and y)
    expected_ellipses = [(3, 2, r, r), (11, 10, r, r), (27, 18, r, r), (19, 10, r, r)]

    assert sorted(painter.ellipses) == sorted(expected_ellipses)

    expected_lines = [MockLine((3, 2), (11, 10)), MockLine((11, 10), (19, 10)),
                      MockLine((19, 10), (27, 18))]

    assert sorted(painter.lines) == sorted(expected_lines)

    x_offset = 5
    y_offset = 15
    expected_texts = [(3 + x_offset, 2 + y_offset, 'A'),
                      (27 + x_offset, 18 + y_offset, 'B'),
                      (15 + x_offset, 10 + y_offset, 'injector_valve')]

    assert sorted(painter.texts) == sorted(expected_texts)
