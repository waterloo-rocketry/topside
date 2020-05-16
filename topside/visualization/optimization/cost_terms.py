import numpy as np


# TODO(jacob): Once vectorization is done, split this into two cost
# terms for better readability.
class NeighboringDistance():
    def __init__(self, g, node_indices, node_component_neighbors, settings):
        self.num_nodes = len(node_indices)

        self.internal_mask = np.ones((self.num_nodes, self.num_nodes))
        self.neighbors_mask = np.ones((self.num_nodes, self.num_nodes))
        
        for node in g:
            i = node_indices[node]
            for neighbor in g.neighbors(node):
                j = node_indices[neighbor]
                if neighbor in node_component_neighbors[node]:
                    self.internal_mask[i, j] = 0
                    self.internal_mask[j, i] = 0
                else:
                    self.neighbors_mask[i, j] = 0
                    self.neighbors_mask[j, i] = 0

        self.internal_weight = settings.internal_weight
        self.neighbors_weight = settings.neighbors_weight
        self.nominal_dist_internal = settings.nominal_dist_internal
        self.nominal_dist_neighbors = settings.nominal_dist_neighbors

    def evaluate(self, costargs):
        cost = 0
        grad = np.zeros(self.num_nodes * 2)

        internal_norms = np.ma.masked_array(costargs['norms'], mask=self.internal_mask)
        neighbors_norms = np.ma.masked_array(costargs['norms'], mask=self.neighbors_mask)

        internal_matrix = self.internal_weight * \
            (self.nominal_dist_internal - internal_norms) ** 2
        cost += np.sum(internal_matrix.filled(0))

        neighbors_matrix = self.neighbors_weight * \
            (self.nominal_dist_neighbors - neighbors_norms) ** 2
        cost += np.sum(neighbors_matrix.filled(0))

        internal_grad_common = self.internal_weight * \
            (internal_norms - self.nominal_dist_internal) * (4 / internal_norms)
        internal_grad_matrix = costargs['deltas'] * internal_grad_common[:, :, None]
        grad += np.reshape(np.sum(internal_grad_matrix.filled(0), axis=1), grad.shape)

        neighbors_grad_common = self.neighbors_weight * \
            (neighbors_norms - self.nominal_dist_neighbors) * (4 / neighbors_norms)
        neighbors_grad_matrix = costargs['deltas'] * neighbors_grad_common[:, :, None]
        grad += np.reshape(np.sum(neighbors_grad_matrix.filled(0), axis=1), grad.shape)

        return (cost, grad)


class NonNeighboringDistance:
    def __init__(self, g, node_indices, node_component_neighbors, settings):
        self.num_nodes = len(node_indices)

        self.nonneighbors_mask = np.identity(self.num_nodes)
        
        for node in g:
            i = node_indices[node]

            for neighbor in g.neighbors(node):
                j = node_indices[neighbor]
                self.nonneighbors_mask[i, j] = 1
                self.nonneighbors_mask[j, i] = 1
        
        self.others_weight = settings.others_weight
        self.minimum_dist_others = settings.minimum_dist_others

    def evaluate(self, costargs):
        cost = 0
        grad = np.zeros(self.num_nodes * 2)

        nodes_to_ignore = (costargs['norms'] >= self.minimum_dist_others)
        mask = np.logical_or(self.nonneighbors_mask, nodes_to_ignore)

        masked_norms = np.ma.masked_array(costargs['norms'], mask=mask)

        cost_matrix = self.others_weight * (self.minimum_dist_others - masked_norms) ** 2
        cost += np.sum(cost_matrix.filled(0))

        grad_mask = np.repeat(mask, 2, axis=np.newaxis)

        grad_common_term = self.others_weight * \
            (masked_norms - self.minimum_dist_others) * (4 / masked_norms)
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
        
        self.centroid_deviation_weight = settings.centroid_deviation_weight
        
        grad_coefficients_diag = self.centroid_deviation_weight * 2 * np.identity(self.num_nodes)
        
        grad_coefficients_off_diag = self.centroid_deviation_weight * -2 * np.ones((self.num_nodes, self.num_nodes, 2)) / self.num_neighbors
        np.fill_diagonal(grad_coefficients_off_diag[:, :, 0], 0)
        np.fill_diagonal(grad_coefficients_off_diag[:, :, 1], 0)
        
        self.grad_coefficients = grad_coefficients_off_diag + grad_coefficients_diag[:, :, None]

    def evaluate(self, costargs):
        cost = 0
        grad = np.zeros(self.num_nodes * 2)

        masked_deltas = np.ma.masked_array(costargs['deltas'], mask=self.cost_mask)
        centroid_deviations = np.sum(masked_deltas, axis=1) / self.num_neighbors

        cost_matrix = self.centroid_deviation_weight * centroid_deviations ** 2
        cost += np.sum(cost_matrix.filled(0))

        reshaped = np.reshape(centroid_deviations, (1, self.num_nodes, 2))
        repeated = np.repeat(reshaped, self.num_nodes, axis=0)

        grad_deviations = np.ma.masked_array(repeated, mask=self.grad_mask)

        grad_matrix = self.grad_coefficients * grad_deviations
        grad += np.reshape(np.sum(grad_matrix.filled(0), axis=1), grad.shape)

        return (cost, grad)


class RightAngleDeviation:
    def __init__(self, g, node_indices, node_component_neighbors, settings):
        self.num_nodes = len(node_indices)

        self.internal_mask = np.ones((self.num_nodes, self.num_nodes, 2))
        for node in g:
            i = node_indices[node]
            for neighbor in node_component_neighbors[node]:
                j = node_indices[neighbor]
                self.internal_mask[i, j] = 0
                self.internal_mask[j, i] = 0

        self.right_angle_weight = settings.right_angle_weight

    def evaluate(self, costargs):
        cost = 0
        grad = np.zeros(self.num_nodes * 2)

        internal_deltas = np.ma.masked_array(costargs['deltas'], mask=self.internal_mask)

        dxdy = np.product(internal_deltas, axis=2)

        cost_matrix = self.right_angle_weight * dxdy ** 2
        cost += np.sum(cost_matrix.filled(0))

        grad_common = self.right_angle_weight * 4 * dxdy[:, :, None]
        grad_matrix = grad_common * np.flip(internal_deltas, axis=2)
        grad += np.reshape(np.sum(grad_matrix.filled(0), axis=1), grad.shape)

        return (cost, grad)


class HorizontalDeviation:
    def __init__(self, g, node_indices, node_component_neighbors, settings):
        self.num_nodes = len(node_indices)
    
        self.internal_mask = np.ones((self.num_nodes, self.num_nodes))
        for node in g:
            i = node_indices[node]
            for neighbor in node_component_neighbors[node]:
                j = node_indices[neighbor]
                self.internal_mask[i, j] = 0
                self.internal_mask[j, i] = 0
        
        self.horizontal_weight = settings.horizontal_weight

    def evaluate(self, costargs):
        cost = 0
        grad = np.zeros(self.num_nodes * 2)

        delta_y = costargs['deltas'][:, :, 1]

        internal_delta_y = np.ma.masked_array(delta_y, mask=self.internal_mask)

        cost_matrix = self.horizontal_weight * internal_delta_y ** 2
        cost += np.sum(cost_matrix.filled(0))

        grad_matrix = np.ma.masked_array(np.zeros((self.num_nodes, self.num_nodes, 2)))
        grad_matrix[:, :, 1] = self.horizontal_weight * 4 * internal_delta_y
        grad += np.reshape(np.sum(grad_matrix.filled(0), axis=1), grad.shape)

        return (cost, grad)
