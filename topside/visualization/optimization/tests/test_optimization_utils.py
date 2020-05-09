import numpy as np

import topside as top


def test_pos_dict_to_vector():
    pos = {0: np.array([1, 2]), 1: np.array([3, 4])}
    node_indices = {0: 0, 1: 1}

    expected = np.transpose([[1, 2, 3, 4]])
    calculated = top.pos_dict_to_vector(pos, node_indices)

    np.testing.assert_array_equal(expected, calculated)


def test_vector_to_pos_dict():
    v = np.transpose([[1, 2, 3, 4]])
    node_indices = {0: 0, 1: 1}

    expected = {0: np.array([1, 2]), 1: np.array([3, 4])}
    calculated = top.vector_to_pos_dict(v, node_indices)

    assert len(expected) == len(calculated)

    for k, v in expected.items():
        assert k in calculated
        np.testing.assert_array_equal(v, calculated[k])
