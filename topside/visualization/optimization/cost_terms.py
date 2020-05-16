import numpy as np


class NeighboringDistance():
    def __init__(self, g, node_indices, node_component_neighbors, settings, internal):
        self.num_nodes = len(node_indices)

        self.mask = np.ones((self.num_nodes, self.num_nodes))

        for node in g:
            i = node_indices[node]
            for neighbor in g.neighbors(node):
                j = node_indices[neighbor]
                if internal is (neighbor in node_component_neighbors[node]):
                    self.mask[i, j] = 0
                    self.mask[j, i] = 0

        if internal:
            self.nominal_dist = settings.nominal_dist_internal
            self.weight = settings.internal_weight
        else:
            self.nominal_dist = settings.nominal_dist_neighbors
            self.weight = settings.neighbors_weight

    def evaluate(self, costargs):
        cost = 0
        grad = np.zeros(self.num_nodes * 2)

        norms = np.ma.masked_array(costargs['norms'], mask=self.mask)

        cost_matrix = self.weight * (self.nominal_dist - norms) ** 2
        cost += np.sum(cost_matrix.filled(0))

        grad_common = self.weight * (norms - self.nominal_dist) * (4 / norms)
        grad_matrix = costargs['deltas'] * grad_common[:, :, None]
        grad += np.reshape(np.sum(grad_matrix.filled(0), axis=1), grad.shape)

        return (cost, grad)


class NonNeighboringDistance:
    def __init__(self, g, node_indices, node_component_neighbors, settings):
        self.num_nodes = len(node_indices)

        self.mask = np.identity(self.num_nodes)

        for node in g:
            i = node_indices[node]

            for neighbor in g.neighbors(node):
                j = node_indices[neighbor]
                self.mask[i, j] = 1
                self.mask[j, i] = 1

        self.weight = settings.others_weight
        self.minimum_dist = settings.minimum_dist_others

    def evaluate(self, costargs):
        cost = 0
        grad = np.zeros(self.num_nodes * 2)

        nodes_to_ignore = (costargs['norms'] >= self.minimum_dist)
        mask = np.logical_or(self.mask, nodes_to_ignore)

        masked_norms = np.ma.masked_array(costargs['norms'], mask=mask)

        cost_matrix = self.weight * (self.minimum_dist - masked_norms) ** 2
        cost += np.sum(cost_matrix.filled(0))

        grad_common_term = self.weight * (masked_norms - self.minimum_dist) * (4 / masked_norms)
        grad_matrix = costargs['deltas'] * grad_common_term[:, :, None]

        grad += np.reshape(np.sum(grad_matrix.filled(0), axis=1), grad.shape)

        return (cost, grad)


class CentroidDeviation:
    def __init__(self, g, node_indices, node_component_neighbors, settings):
        self.num_nodes = len(node_indices)

        self.cost_mask = np.ones((self.num_nodes, self.num_nodes, 2))
        self.grad_mask = np.ones((self.num_nodes, self.num_nodes, 2))
        self.num_neighbors = np.ones((self.num_nodes, 1))

        for node in g:
            i = node_indices[node]
            neighbors = list(g.neighbors(node))
            if len(neighbors) > 1:
                self.grad_mask[i, i] = 0
                self.num_neighbors[i] = len(neighbors)
                for neighbor in neighbors:
                    j = node_indices[neighbor]
                    self.cost_mask[i, j] = 0
                    self.grad_mask[j, i] = 0

        self.weight = settings.centroid_deviation_weight

        grad_coeffs_diag = self.weight * 2 * np.identity(self.num_nodes)

        grad_coeffs_off_diag = self.weight * -2 * \
            np.ones((self.num_nodes, self.num_nodes, 2)) / self.num_neighbors
        np.fill_diagonal(grad_coeffs_off_diag[:, :, 0], 0)
        np.fill_diagonal(grad_coeffs_off_diag[:, :, 1], 0)

        self.grad_coeffs = grad_coeffs_off_diag + grad_coeffs_diag[:, :, None]

    def evaluate(self, costargs):
        cost = 0
        grad = np.zeros(self.num_nodes * 2)

        masked_deltas = np.ma.masked_array(costargs['deltas'], mask=self.cost_mask)
        centroid_deviations = np.sum(masked_deltas, axis=1) / self.num_neighbors

        cost_matrix = self.weight * centroid_deviations ** 2
        cost += np.sum(cost_matrix.filled(0))

        reshaped = np.reshape(centroid_deviations, (1, self.num_nodes, 2))
        repeated = np.repeat(reshaped, self.num_nodes, axis=0)

        grad_deviations = np.ma.masked_array(repeated, mask=self.grad_mask)

        grad_matrix = self.grad_coeffs * grad_deviations
        grad += np.reshape(np.sum(grad_matrix.filled(0), axis=1), grad.shape)

        return (cost, grad)


class RightAngleDeviation:
    def __init__(self, g, node_indices, node_component_neighbors, settings):
        self.num_nodes = len(node_indices)

        self.mask = np.ones((self.num_nodes, self.num_nodes, 2))
        for node in g:
            i = node_indices[node]
            for neighbor in node_component_neighbors[node]:
                j = node_indices[neighbor]
                self.mask[i, j] = 0
                self.mask[j, i] = 0

        self.weight = settings.right_angle_weight

    def evaluate(self, costargs):
        cost = 0
        grad = np.zeros(self.num_nodes * 2)

        internal_deltas = np.ma.masked_array(costargs['deltas'], mask=self.mask)

        dxdy = np.product(internal_deltas, axis=2)

        cost_matrix = self.weight * dxdy ** 2
        cost += np.sum(cost_matrix.filled(0))

        grad_common = self.weight * 4 * dxdy[:, :, None]
        grad_matrix = grad_common * np.flip(internal_deltas, axis=2)
        grad += np.reshape(np.sum(grad_matrix.filled(0), axis=1), grad.shape)

        return (cost, grad)


class HorizontalDeviation:
    def __init__(self, g, node_indices, node_component_neighbors, settings):
        self.num_nodes = len(node_indices)

        self.mask = np.ones((self.num_nodes, self.num_nodes))
        for node in g:
            i = node_indices[node]
            for neighbor in node_component_neighbors[node]:
                j = node_indices[neighbor]
                self.mask[i, j] = 0
                self.mask[j, i] = 0

        self.weight = settings.horizontal_weight

    def evaluate(self, costargs):
        cost = 0
        grad = np.zeros(self.num_nodes * 2)

        delta_y = costargs['deltas'][:, :, 1]

        internal_delta_y = np.ma.masked_array(delta_y, mask=self.mask)

        cost_matrix = self.weight * internal_delta_y ** 2
        cost += np.sum(cost_matrix.filled(0))

        grad_matrix = np.ma.masked_array(np.zeros((self.num_nodes, self.num_nodes, 2)))
        grad_matrix[:, :, 1] = self.weight * 4 * internal_delta_y
        grad += np.reshape(np.sum(grad_matrix.filled(0), axis=1), grad.shape)

        return (cost, grad)
