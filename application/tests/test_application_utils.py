import pytest

from ..visualization_area import get_positioning_params


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
