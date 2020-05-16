import networkx as nx
import numpy as np

import topside as top


def make_one_component_engine_data():
    g = nx.Graph([(1, 'c1.1'), ('c1.1', 'c1.2'), ('c1.2', 2)])
    node_indices = {1: 0, 'c1.1': 1, 'c1.2': 2, 2: 3}
    neighbors = {1: [], 'c1.1': ['c1.2'], 'c1.2': ['c1.1'], 2: []}

    return g, node_indices, neighbors


def make_two_component_engine_data():
    g = nx.Graph([(1, 'c1.1'), (1, 'c2.1'), ('c1.1', 'c1.2'),
                  ('c2.1', 'c2.2'), ('c1.2', 2), ('c2.2', 2)])
    node_indices = {1: 0, 'c1.1': 1, 'c2.1': 2, 'c1.2': 3, 'c2.2': 4,  2: 5}
    neighbors = {'c1.1': ['c1.2'], 'c1.2': ['c1.1'],
                 'c2.1': ['c2.2'], 'c2.2': ['c2.1'], 1: [], 2: []}

    return g, node_indices, neighbors


def test_neighboring_distance_cost_internal_zero():
    g, node_indices, neighbors = make_one_component_engine_data()
    settings = top.OptimizerSettings(neighbors_weight=0,
                                     nominal_dist_internal=7,
                                     internal_weight=1)

    x = np.array([
        [0, 0],
        [10, 10],
        [10, 17],
        [30, 30]
    ]).reshape((-1, 1))

    expected_cost = 0
    expected_grad = np.zeros(8)

    ct = top.NeighboringDistance(g, node_indices, neighbors, settings)
    cost, grad = ct.evaluate(x)

    assert cost == expected_cost
    np.testing.assert_equal(expected_grad, grad)


def test_neighboring_distance_cost_internal_nonzero():
    g, node_indices, neighbors = make_one_component_engine_data()
    settings = top.OptimizerSettings(neighbors_weight=0,
                                     nominal_dist_internal=7,
                                     internal_weight=1)

    x = np.array([
        [0, 0],
        [10, 10],
        [13, 14],
        [30, 30]
    ]).reshape((-1, 1))

    expected_cost = 8  # 2 nodes * (D - sqrt( (x2-x1)^2 + (y2-y1)^2 ))^2 per node

    common = 2 * -2 * (7 - 5) / 5  # 2 nodes * (-2 * (D - norm) / norm) per node
    expected_grad = np.array([
        [0, 0],
        [common * -3, common * -4],
        [common * 3, common * 4],
        [0, 0]
    ]).flatten()

    ct = top.NeighboringDistance(g, node_indices, neighbors, settings)
    cost, grad = ct.evaluate(x)

    assert cost == expected_cost
    np.testing.assert_equal(expected_grad, grad)


def test_neighboring_distance_cost_external_zero():
    g, node_indices, neighbors = make_one_component_engine_data()
    settings = top.OptimizerSettings(nominal_dist_neighbors=10,
                                     neighbors_weight=1,
                                     internal_weight=0)

    x = np.array([
        [0, 0],
        [10, 0],
        [10, 5],
        [20, 5]
    ]).reshape((-1, 1))

    expected_cost = 0
    expected_grad = np.zeros(8)

    ct = top.NeighboringDistance(g, node_indices, neighbors, settings)
    cost, grad = ct.evaluate(x)

    assert cost == expected_cost
    np.testing.assert_equal(expected_grad, grad)


def test_neighboring_distance_cost_external_nonzero():
    g, node_indices, neighbors = make_one_component_engine_data()
    settings = top.OptimizerSettings(nominal_dist_neighbors=10,
                                     neighbors_weight=1,
                                     internal_weight=0)

    x = np.array([
        [0, 0],
        [3, 4],
        [13, 14],
        [16, 18]
    ]).reshape((-1, 1))

    expected_cost = 100  # 4 nodes * (D - sqrt( (x2-x1)^2 + (y2-y1)^2 ))^2 per node

    common = 2 * -2 * (10 - 5) / 5  # 2 nodes * (-2 * (D - norm) / norm) per node
    expected_grad = np.array([
        [common * -3, common * -4],
        [common * 3, common * 4],
        [common * -3, common * -4],
        [common * 3, common * 4]
    ]).flatten()

    ct = top.NeighboringDistance(g, node_indices, neighbors, settings)
    cost, grad = ct.evaluate(x)

    assert cost == expected_cost
    np.testing.assert_equal(expected_grad, grad)


def test_nonneighboring_distance_cost_close():
    g, node_indices, neighbors = make_one_component_engine_data()
    settings = top.OptimizerSettings(minimum_dist_others=10,
                                     others_weight=1)

    x = np.array([
        [0, 0],
        [0, 100],
        [100, 100],
        [3, 4]
    ]).reshape((-1, 1))

    expected_cost = 50  # 2 nodes * (D - sqrt( (x2-x1)^2 + (y2-y1)^2 ))^2 per node

    common = 2 * -2 * (10 - 5) / 5  # 2 nodes * (-2 * (D - norm) / norm) per node
    expected_grad = np.array([
        [common * -3, common * -4],
        [0, 0],
        [0, 0],
        [common * 3, common * 4]
    ]).flatten()

    ct = top.NonNeighboringDistance(g, node_indices, neighbors, settings)
    cost, grad = ct.evaluate(x)

    assert cost == expected_cost
    np.testing.assert_equal(expected_grad, grad)


def test_nonneighboring_distance_cost_right_at_boundary():
    g, node_indices, neighbors = make_one_component_engine_data()
    settings = top.OptimizerSettings(minimum_dist_others=10,
                                     others_weight=1)

    x = np.array([
        [0, 0],
        [0, 100],
        [100, 100],
        [0, 10]
    ]).reshape((-1, 1))

    expected_cost = 0
    expected_grad = np.zeros(8)

    ct = top.NonNeighboringDistance(g, node_indices, neighbors, settings)
    cost, grad = ct.evaluate(x)

    assert cost == expected_cost
    np.testing.assert_equal(expected_grad, grad)


def test_nonneighboring_distance_cost_far():
    g, node_indices, neighbors = make_one_component_engine_data()
    settings = top.OptimizerSettings(minimum_dist_others=10,
                                     others_weight=1)

    x = np.array([
        [0, 0],
        [0, 100],
        [100, 100],
        [100, 200]
    ]).reshape((-1, 1))

    expected_cost = 0
    expected_grad = np.zeros(8)

    ct = top.NonNeighboringDistance(g, node_indices, neighbors, settings)
    cost, grad = ct.evaluate(x)

    assert cost == expected_cost
    np.testing.assert_equal(expected_grad, grad)


def test_nonneighboring_distance_cost_multiple_nodes_far():
    g, node_indices, neighbors = make_two_component_engine_data()
    settings = top.OptimizerSettings(minimum_dist_others=10,
                                     others_weight=1)

    x = np.array([
        [0, 0],
        [10, 0],
        [10, 100],
        [20, 0],
        [20, 100],
        [30, 0]
    ]).reshape((-1, 1))

    expected_cost = 0
    expected_grad = np.zeros(12)

    ct = top.NonNeighboringDistance(g, node_indices, neighbors, settings)
    cost, grad = ct.evaluate(x)

    assert cost == expected_cost
    np.testing.assert_equal(expected_grad, grad)


def test_nonneighboring_distance_cost_multiple_nodes_close():
    g, node_indices, neighbors = make_two_component_engine_data()
    settings = top.OptimizerSettings(minimum_dist_others=20,
                                     others_weight=1)

    x = np.array([
        [0, 0],    # 1
        [100, 0],  # c1.1
        [103, 4],  # c2.1
        [106, 1],  # c1.2
        [109, 5],  # c2.2
        [200, 0]   # 2
    ]).reshape((-1, 1))

    cost_11_21 = 2 * (20 - 5) ** 2
    cost_11_22 = 2 * (20 - np.sqrt(106)) ** 2
    cost_12_21 = 2 * (20 - np.sqrt(18)) ** 2
    cost_12_22 = 2 * (20 - 5) ** 2
    expected_cost = cost_11_21 + cost_11_22 + cost_12_21 + cost_12_22

    # 2 nodes * (-2 * (D - norm) / norm) per node
    common_11_21 = 2 * -2 * (20 - 5) / 5
    common_11_22 = 2 * -2 * (20 - np.sqrt(106)) / np.sqrt(106)
    common_12_21 = 2 * -2 * (20 - np.sqrt(18)) / np.sqrt(18)
    common_12_22 = 2 * -2 * (20 - 5) / 5

    expected_grad = np.array([
        [0, 0],
        [common_11_21 * -3 + common_11_22 * -9, common_11_21 * -4 + common_11_22 * -5],
        [common_11_21 * 3 + common_12_21 * -3, common_11_21 * 4 + common_12_21 * 3],
        [common_12_21 * 3 + common_12_22 * -3, common_12_21 * -3 + common_12_22 * -4],
        [common_11_22 * 9 + common_12_22 * 3, common_11_22 * 5 + common_12_22 * 4],
        [0, 0]
    ]).flatten()

    ct = top.NonNeighboringDistance(g, node_indices, neighbors, settings)
    cost, grad = ct.evaluate(x)

    assert cost == expected_cost
    np.testing.assert_equal(expected_grad, grad)


def test_centroid_deviation_cost_term_zero():
    g, node_indices, neighbors = make_one_component_engine_data()
    settings = top.OptimizerSettings(centroid_deviation_weight=1)

    x = np.array([
        [0, 0],
        [1, 0],
        [2, 0],
        [3, 0]
    ]).reshape((-1, 1))

    expected_cost = 0
    expected_grad = np.zeros(8)

    ct = top.CentroidDeviation(g, node_indices, neighbors, settings)
    cost, grad = ct.evaluate(x)

    assert cost == expected_cost
    np.testing.assert_equal(expected_grad, grad)


def test_centroid_deviation_cost_term_nonzero_end_node_x():
    g, node_indices, neighbors = make_one_component_engine_data()
    settings = top.OptimizerSettings(centroid_deviation_weight=1)

    x = np.array([
        [4, 0],
        [10, 0],
        [12, 0],
        [14, 0]
    ]).reshape((-1, 1))

    expected_cost = 4  # Only node [10, 0] will incur cost (deviation of 2 in x)
    common = 10 - (4 + 12) / 2  # x - mean(x_neighbors)
    expected_grad = np.array([
        [-common, 0],
        [2*common, 0],
        [-common, 0],
        [0, 0]
    ]).flatten()

    ct = top.CentroidDeviation(g, node_indices, neighbors, settings)
    cost, grad = ct.evaluate(x)

    assert cost == expected_cost
    np.testing.assert_equal(expected_grad, grad)


def test_centroid_deviation_cost_term_nonzero_end_node_y():
    g, node_indices, neighbors = make_one_component_engine_data()
    settings = top.OptimizerSettings(centroid_deviation_weight=1)

    x = np.array([
        [0, 16],
        [0, 10],
        [0, 8],
        [0, 6]
    ]).reshape((-1, 1))

    expected_cost = 4  # Only node [0, 10] will incur cost (deviation of -2 in y)
    common = 10 - (16 + 8) / 2  # y - mean(y_neighbors)
    expected_grad = np.array([
        [0, -common],
        [0, 2*common],
        [0, -common],
        [0, 0]
    ]).flatten()

    ct = top.CentroidDeviation(g, node_indices, neighbors, settings)
    cost, grad = ct.evaluate(x)

    assert cost == expected_cost
    np.testing.assert_equal(expected_grad, grad)


def test_centroid_deviation_cost_term_nonzero_end_node_xy():
    g, node_indices, neighbors = make_one_component_engine_data()
    settings = top.OptimizerSettings(centroid_deviation_weight=1)

    x = np.array([
        [6, 14],
        [16, 16],
        [22, 22],
        [28, 28]
    ]).reshape((-1, 1))

    expected_cost = 8  # Only node [16, 16] will incur cost (deviation of 2 in x, -2 in y)
    common_x = 16 - (22 + 6) / 2  # x - mean(x_neighbors)
    common_y = 16 - (22 + 14) / 2  # y - mean(y_neighbors)
    expected_grad = np.array([
        [-common_x, -common_y],
        [2*common_x, 2*common_y],
        [-common_x, -common_y],
        [0, 0]
    ]).flatten()

    ct = top.CentroidDeviation(g, node_indices, neighbors, settings)
    cost, grad = ct.evaluate(x)

    assert cost == expected_cost
    np.testing.assert_equal(expected_grad, grad)


def test_centroid_deviation_cost_term_nonzero_interior_node_x():
    g, node_indices, neighbors = make_one_component_engine_data()
    settings = top.OptimizerSettings(centroid_deviation_weight=1)

    x = np.array([
        [40, 0],
        [30, 0],
        [16, 0],
        [10, 0]
    ]).reshape((-1, 1))

    expected_cost = 20  # (28-30)^2 = 4 for [30, 0] + (20-16)^2 = 16 for [16, 0]
    common_1 = 30 - (40 + 16) / 2  # y - mean(y_neighbors)
    common_2 = 16 - (30 + 10) / 2  # y - mean(y_neighbors)
    expected_grad = np.array([
        [-common_1, 0],
        [2*common_1 - common_2, 0],
        [2*common_2 - common_1, 0],
        [-common_2, 0]
    ]).flatten()

    ct = top.CentroidDeviation(g, node_indices, neighbors, settings)
    cost, grad = ct.evaluate(x)

    assert cost == expected_cost
    np.testing.assert_equal(expected_grad, grad)


def test_centroid_deviation_cost_term_nonzero_interior_node_y():
    g, node_indices, neighbors = make_one_component_engine_data()
    settings = top.OptimizerSettings(centroid_deviation_weight=1)

    x = np.array([
        [0, 0],
        [0, 6],
        [0, 20],
        [0, 30]
    ]).reshape((-1, 1))

    expected_cost = 20  # (10-6)^2 = 16 for [0, 6] + (18-20)^2 = 4 for [0, 20]
    common_1 = 6 - (20 + 0) / 2  # y - mean(y_neighbors)
    common_2 = 20 - (30 + 6) / 2  # y - mean(y_neighbors)
    expected_grad = np.array([
        [0, -common_1],
        [0, 2*common_1 - common_2],
        [0, 2*common_2 - common_1],
        [0, -common_2]
    ]).flatten()

    ct = top.CentroidDeviation(g, node_indices, neighbors, settings)
    cost, grad = ct.evaluate(x)

    assert cost == expected_cost
    np.testing.assert_equal(expected_grad, grad)


def test_centroid_deviation_cost_term_nonzero_interior_node_xy():
    g, node_indices, neighbors = make_one_component_engine_data()
    settings = top.OptimizerSettings(centroid_deviation_weight=1)

    x = np.array([
        [10, 10],
        [16, 24],
        [30, 30],
        [40, 40]
    ]).reshape((-1, 1))

    expected_cost_x = 20  # (20-16)^2 = 16 for [16, 24] + (30-28)^2 = 4 for [30, 30]
    expected_cost_y = 20  # (20-24)^2 = 16 for [16, 24] + (30-32)^2 = 4 for [30, 30]
    expected_cost = expected_cost_x + expected_cost_y

    common_x_1 = 16 - (30 + 10) / 2  # x - mean(x_neighbors)
    common_x_2 = 30 - (40 + 16) / 2  # x - mean(x_neighbors)
    common_y_1 = 24 - (30 + 10) / 2  # y - mean(y_neighbors)
    common_y_2 = 30 - (40 + 24) / 2  # y - mean(y_neighbors)
    expected_grad = np.array([
        [-common_x_1, -common_y_1],
        [2*common_x_1 - common_x_2, 2*common_y_1 - common_y_2],
        [2*common_x_2 - common_x_1, 2*common_y_2 - common_y_1],
        [-common_x_2, -common_y_2]
    ]).flatten()

    ct = top.CentroidDeviation(g, node_indices, neighbors, settings)
    cost, grad = ct.evaluate(x)

    assert cost == expected_cost
    np.testing.assert_equal(expected_grad, grad)


def test_right_angle_deviation_cost_zero_horizontal():
    g, node_indices, neighbors = make_one_component_engine_data()
    settings = top.OptimizerSettings(right_angle_weight=1)

    x = np.array([
        [0, 0],
        [5, 3],
        [6, 3],
        [10, 10]
    ]).reshape((-1, 1))

    expected_cost = 0
    expected_grad = np.array([
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0]
    ]).flatten()

    ct = top.RightAngleDeviation(g, node_indices, neighbors, settings)
    cost, grad = ct.evaluate(x)

    assert cost == expected_cost
    np.testing.assert_equal(expected_grad, grad)


def test_right_angle_deviation_cost_zero_vertical():
    g, node_indices, neighbors = make_one_component_engine_data()
    settings = top.OptimizerSettings(right_angle_weight=1)

    x = np.array([
        [0, 0],
        [5, 3],
        [5, 4],
        [10, 10]
    ]).reshape((-1, 1))

    expected_cost = 0
    expected_grad = np.array([
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0]
    ]).flatten()

    ct = top.RightAngleDeviation(g, node_indices, neighbors, settings)
    cost, grad = ct.evaluate(x)

    assert cost == expected_cost
    np.testing.assert_equal(expected_grad, grad)


def test_right_angle_deviation_cost_nonzero():
    g, node_indices, neighbors = make_one_component_engine_data()
    settings = top.OptimizerSettings(right_angle_weight=1)

    x = np.array([
        [0, 0],
        [3, 4],
        [7, 6],
        [10, 10]
    ]).reshape((-1, 1))

    expected_cost = 128  # 2 nodes * ((6-4)(7-3))^2 per node

    common = 2 * 2 * (7 - 3) * (6 - 4)  # 2 nodes * 2(x2-x1)(y2-y1) per node
    expected_grad = np.array([
        [0, 0],
        [-2*common, -4*common],
        [2*common, 4*common],
        [0, 0]
    ]).flatten()

    ct = top.RightAngleDeviation(g, node_indices, neighbors, settings)
    cost, grad = ct.evaluate(x)

    assert cost == expected_cost
    np.testing.assert_equal(expected_grad, grad)


def test_horizontal_deviation_cost_zero():
    g, node_indices, neighbors = make_one_component_engine_data()
    settings = top.OptimizerSettings(horizontal_weight=1)

    x = np.array([
        [0, 0],
        [5, 3],
        [6, 3],
        [10, 10]
    ]).reshape((-1, 1))

    expected_cost = 0
    expected_grad = np.array([
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0]
    ]).flatten()

    cost, grad = top.horizontal_deviation_cost_term(x, g, node_indices, neighbors, settings)

    assert cost == expected_cost
    np.testing.assert_equal(expected_grad, grad)


def test_horizontal_deviation_cost_nonzero():
    g, node_indices, neighbors = make_one_component_engine_data()
    settings = top.OptimizerSettings(horizontal_weight=1)

    x = np.array([
        [0, 0],
        [5, 3],
        [6, 5],
        [10, 10]
    ]).reshape((-1, 1))

    expected_cost = 8  # 2 nodes * (5 - 3)^2 per node
    expected_grad = np.array([
        [0, 0],
        [0, -8],
        [0, 8],
        [0, 0]
    ]).flatten()

    cost, grad = top.horizontal_deviation_cost_term(x, g, node_indices, neighbors, settings)

    assert cost == expected_cost
    np.testing.assert_equal(expected_grad, grad)
