from dataclasses import dataclass


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
        return isinstance(other, MockLine) and \
            ((self.p1 == other.p1 and self.p2 == other.p2) or
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

    def pen(self):
        return None

    def setFont(self, font):
        pass

    def drawEllipse(self, center, rx, ry):
        self.ellipses.append((center.x(), center.y(), rx, ry))

    def drawLine(self, x1, y1, x2, y2):
        self.lines.append(MockLine((x1, y1), (x2, y2)))

    def drawText(self, x, y, text):
        self.texts.append((x, y, text))

    def clear(self):
        self.ellipses = []
        self.lines = []
        self.texts = []
