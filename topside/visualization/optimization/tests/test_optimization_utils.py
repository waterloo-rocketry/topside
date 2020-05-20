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


def test_make_costargs():
    x = np.array([
        [0, 0],
        [3, 4],
        [13, 14],
        [17, 17]
    ]).reshape((-1, 1))

    expected_deltas = np.array([
        [[0, 0], [-3, -4], [-13, -14], [-17, -17]],
        [[3, 4], [0, 0], [-10, -10], [-14, -13]],
        [[13, 14], [10, 10], [0, 0], [-4, -3]],
        [[17, 17], [14, 13], [4, 3], [0, 0]]
    ])

    expected_norms = np.array([
        [0, 5, np.sqrt(13**2 + 14**2), np.sqrt(2 * 17**2)],
        [5, 0, np.sqrt(200), np.sqrt(14**2 + 13**2)],
        [np.sqrt(13**2 + 14**2), np.sqrt(200), 0, 5],
        [np.sqrt(2 * 17**2), np.sqrt(14**2 + 13**2), 5, 0]
    ])

    costargs = top.make_costargs(x)

    np.testing.assert_equal(expected_deltas, costargs['deltas'])
    np.testing.assert_equal(expected_norms, costargs['norms'])
