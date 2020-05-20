import numpy as np


class NeighboringDistance():
    """
    Encourages a nominal distance between neighboring nodes.

    For two nodes [x1, y1] and [x2, y2] with nominal separation D, the
    neighboring distance cost C is defined as:

        C = W * (D - sqrt((x2 - x1)^2 + (y2 - y1)^2))^2

    where W is a constant used to scale the relative "importance" of
    this cost term.
    """

    def __init__(self, g, node_indices, node_component_neighbors, settings, internal):
        """
        Initialize the cost term.

        Parameters
        ----------

        g: graph
            The graph for which this cost term will be evaluated.
            Typically, this is a NetworkX graph, but it can be any type
            with a .neighbors(n) method returning the neighbors of node
            n. Calling this directly with a PlumbingEngine graph may
            lead to unexpected results; it is best to use a terminal
            graph instead (topside.terminal_graph).

        node_indices: dict
            Dict where node_indices[n] is the index i of node n in the
            cost vector.

        node_component_neighbors: dict
            Dict where, for a given node n, node_component_neighbors[n]
            is a list of all nodes in g that are both neighbors of n
            and in the same component as n.

        settings: OptimizerSettings
            This can be any type that provides the same attributes as
            topside.visualization.optimization.OptimizerSettings.

        internal: bool
            if True, this cost term penalizes only deviation from
            nominal distance within a component. If False, this cost
            term instead penalizes deviation from nominal distance
            between two nodes that are not part of the same component.
        """

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
        """
        Evaluate the cost term and return a tuple of (cost, gradient).

        Arguments:

        costargs: dict
            Expected to contain:
            - 'deltas': N x N x 2 numpy array, where:
                deltas[i, j, :] == [xj - xi, yj - yi]
            - 'norms': N x N numpy array, where:
                norms[i, j] == sqrt[(xj - xi)^2 + (yj - yi)^2]
        """
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
    """
    Encourages a minimum distance between non-neighboring nodes.

    For two nodes [x1, y1] and [x2, y2] with minimum separation D, the
    non-neighboring distance cost C can be calculated with the following
    pseudocode algorithm:

        d = sqrt((x2 - x1)^2 + (y2 - y1)^2)

        if d < D:
            C = W * (D - d)^2
        else:
            C = 0

    where W is a constant used to scale the relative "importance" of
    this cost term.
    """

    def __init__(self, g, node_indices, node_component_neighbors, settings):
        """
        Initialize the cost term.

        Parameters
        ----------

        g: graph
            The graph for which this cost term will be evaluated.
            Typically, this is a NetworkX graph, but it can be any type
            with a .neighbors(n) method returning the neighbors of node
            n. Calling this directly with a PlumbingEngine graph may
            lead to unexpected results; it is best to use a terminal
            graph instead (topside.terminal_graph).

        node_indices: dict
            Dict where node_indices[n] is the index i of node n in the
            cost vector.

        node_component_neighbors: dict
            Dict where, for a given node n, node_component_neighbors[n]
            is a list of all nodes in g that are both neighbors of n
            and in the same component as n.

        settings: OptimizerSettings
            This can be any type that provides the same attributes as
            topside.visualization.optimization.OptimizerSettings.
        """
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
        """
        Evaluate the cost term and return a tuple of (cost, gradient).

        Arguments:

        costargs: dict
            Expected to contain:
            - 'deltas': N x N x 2 numpy array, where:
                deltas[i, j, :] == [xj - xi, yj - yi]
            - 'norms': N x N numpy array, where:
                norms[i, j] == sqrt[(xj - xi)^2 + (yj - yi)^2]
        """
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
    """
    Encourages a node to remain close to the centroid of its neighbors.

    The centroid deviation cost term C can be calculated with the
    following pseudocode algorithm:

    if num_neighbors(n) < 2:
        C = 0
    else:
        v = centroid(neighbors(n))
        C = W * ((vx - nx)^2 + (vy - ny)^2)

    where W is a constant used to scale the relative "importance" of
    this cost term.
    """

    def __init__(self, g, node_indices, node_component_neighbors, settings):
        """
        Initialize the cost term.

        Parameters
        ----------

        g: graph
            The graph for which this cost term will be evaluated.
            Typically, this is a NetworkX graph, but it can be any type
            with a .neighbors(n) method returning the neighbors of node
            n. Calling this directly with a PlumbingEngine graph may
            lead to unexpected results; it is best to use a terminal
            graph instead (topside.terminal_graph).

        node_indices: dict
            Dict where node_indices[n] is the index i of node n in the
            cost vector.

        node_component_neighbors: dict
            Dict where, for a given node n, node_component_neighbors[n]
            is a list of all nodes in g that are both neighbors of n
            and in the same component as n.

        settings: OptimizerSettings
            This can be any type that provides the same attributes as
            topside.visualization.optimization.OptimizerSettings.
        """
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
        """
        Evaluate the cost term and return a tuple of (cost, gradient).

        Arguments:

        costargs: dict
            Expected to contain:
            - 'deltas': N x N x 2 numpy array, where:
                deltas[i, j, :] == [xj - xi, yj - yi]
            - 'norms': N x N numpy array, where:
                norms[i, j] == sqrt[(xj - xi)^2 + (yj - yi)^2]
        """
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
    """
    Encourages a component to be oriented horizontally or vertically.

    The right angle deviation cost term C is defined as follows:

    C = W * (x2 - x1)^2 * (y2 - y1)^2

    where W is a constant used to scale the relative "importance" of
    this cost term.
    """

    def __init__(self, g, node_indices, node_component_neighbors, settings):
        """
        Initialize the cost term.

        Parameters
        ----------

        g: graph
            The graph for which this cost term will be evaluated.
            Typically, this is a NetworkX graph, but it can be any type
            with a .neighbors(n) method returning the neighbors of node
            n. Calling this directly with a PlumbingEngine graph may
            lead to unexpected results; it is best to use a terminal
            graph instead (topside.terminal_graph).

        node_indices: dict
            Dict where node_indices[n] is the index i of node n in the
            cost vector.

        node_component_neighbors: dict
            Dict where, for a given node n, node_component_neighbors[n]
            is a list of all nodes in g that are both neighbors of n
            and in the same component as n.

        settings: OptimizerSettings
            This can be any type that provides the same attributes as
            topside.visualization.optimization.OptimizerSettings.
        """
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
        """
        Evaluate the cost term and return a tuple of (cost, gradient).

        Arguments:

        costargs: dict
            Expected to contain:
            - 'deltas': N x N x 2 numpy array, where:
                deltas[i, j, :] == [xj - xi, yj - yi]
            - 'norms': N x N numpy array, where:
                norms[i, j] == sqrt[(xj - xi)^2 + (yj - yi)^2]
        """
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
    """
    Encourages a component to be oriented horizontally.

    The right angle deviation cost term C is defined as follows:

    C = W * (y2 - y1)^2

    where W is a constant used to scale the relative "importance" of
    this cost term.
    """

    def __init__(self, g, node_indices, node_component_neighbors, settings):
        """
        Initialize the cost term.

        Parameters
        ----------

        g: graph
            The graph for which this cost term will be evaluated.
            Typically, this is a NetworkX graph, but it can be any type
            with a .neighbors(n) method returning the neighbors of node
            n. Calling this directly with a PlumbingEngine graph may
            lead to unexpected results; it is best to use a terminal
            graph instead (topside.terminal_graph).

        node_indices: dict
            Dict where node_indices[n] is the index i of node n in the
            cost vector.

        node_component_neighbors: dict
            Dict where, for a given node n, node_component_neighbors[n]
            is a list of all nodes in g that are both neighbors of n
            and in the same component as n.

        settings: OptimizerSettings
            This can be any type that provides the same attributes as
            topside.visualization.optimization.OptimizerSettings.
        """
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
        """
        Evaluate the cost term and return a tuple of (cost, gradient).

        Arguments:

        costargs: dict
            Expected to contain:
            - 'deltas': N x N x 2 numpy array, where:
                deltas[i, j, :] == [xj - xi, yj - yi]
            - 'norms': N x N numpy array, where:
                norms[i, j] == sqrt[(xj - xi)^2 + (yj - yi)^2]
        """
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
