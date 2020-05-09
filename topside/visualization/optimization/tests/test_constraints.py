import numpy as np

import topside as top


def make_simple_position_vector():
    x = np.array([
        [1, 1],
        [1, 2],
        [2, 1],
        [5, 10],
        [1, 1]
    ])
    return np.reshape(x, (-1, 1))


def test_right_angle_constraint_same_point():
    x = make_simple_position_vector()

    assert top.right_angle_cons_f(0, 4, x) == 0
    assert top.right_angle_cons_f(4, 0, x) == 0


def test_right_angle_constraint_same_x():
    x = make_simple_position_vector()

    assert top.right_angle_cons_f(0, 1, x) == 0
    assert top.right_angle_cons_f(1, 0, x) == 0


def test_right_angle_constraint_same_y():
    x = make_simple_position_vector()

    assert top.right_angle_cons_f(0, 2, x) == 0
    assert top.right_angle_cons_f(2, 0, x) == 0


def test_right_angle_constraint_different_x_and_y():
    x = make_simple_position_vector()

    assert top.right_angle_cons_f(0, 3, x) == 36
    assert top.right_angle_cons_f(3, 0, x) == 36


def test_right_angle_constraint_grad_same_point():
    x = make_simple_position_vector()

    expected_grad = np.zeros((1, 10))

    np.testing.assert_array_equal(expected_grad, top.right_angle_cons_j(0, 4, x))
    np.testing.assert_array_equal(expected_grad, top.right_angle_cons_j(4, 0, x))


def test_right_angle_constraint_grad_different_y():
    x = make_simple_position_vector()

    expected_grad = np.zeros((1, 10))
    expected_grad[0, 0] = -1
    expected_grad[0, 2] = 1

    np.testing.assert_array_equal(expected_grad, top.right_angle_cons_j(0, 1, x))
    np.testing.assert_array_equal(expected_grad, top.right_angle_cons_j(1, 0, x))


def test_right_angle_constraint_grad_different_x():
    x = make_simple_position_vector()

    expected_grad = np.zeros((1, 10))
    expected_grad[0, 1] = -1
    expected_grad[0, 5] = 1

    np.testing.assert_array_equal(expected_grad, top.right_angle_cons_j(0, 2, x))
    np.testing.assert_array_equal(expected_grad, top.right_angle_cons_j(2, 0, x))


def test_right_angle_constraint_grad_different_x_and_y():
    x = make_simple_position_vector()

    expected_grad = np.zeros((1, 10))
    expected_grad[0, 0] = -9
    expected_grad[0, 1] = -4
    expected_grad[0, 6] = 9
    expected_grad[0, 7] = 4

    np.testing.assert_array_equal(expected_grad, top.right_angle_cons_j(0, 3, x))
    np.testing.assert_array_equal(expected_grad, top.right_angle_cons_j(3, 0, x))


def test_right_angle_constraint_hess_same_point():
    x = make_simple_position_vector()

    expected_hess = np.zeros((10, 10))

    expected_hess[0, 1] = 1
    expected_hess[1, 0] = 1
    expected_hess[0, 9] = -1
    expected_hess[9, 0] = -1
    expected_hess[8, 1] = -1
    expected_hess[1, 8] = -1
    expected_hess[8, 9] = 1
    expected_hess[9, 8] = 1

    np.testing.assert_array_equal(expected_hess, top.right_angle_cons_h(0, 4, x, None))
    np.testing.assert_array_equal(expected_hess, top.right_angle_cons_h(4, 0, x, None))
