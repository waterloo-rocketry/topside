import numpy as np


# TODO(jacob): Vectorize all of these for (hopefully) significant
# speedup.

# TODO(jacob): Once vectorization is done, split this into two cost
# terms for better readability.
def neighboring_distance_cost_term(x, g, node_indices, node_component_neighbors, settings):
    xr = np.reshape(x, (-1, 2))

    cost = 0
    grad = np.zeros(x.shape[0])

    internal_mask = np.ones((xr.shape[0], xr.shape[0]))
    neighbors_mask = np.ones((xr.shape[0], xr.shape[0]))
    for node in g:
        i = node_indices[node]
        for neighbor in g.neighbors(node):
            j = node_indices[neighbor]
            if neighbor in node_component_neighbors[node]:
                internal_mask[i, j] = 0
                internal_mask[j, i] = 0
            else:
                neighbors_mask[i, j] = 0
                neighbors_mask[j, i] = 0

    deltas = xr[:, None, :] - xr[None, :, :]
    norms = np.linalg.norm(deltas, axis=2)

    internal_norms = np.ma.masked_array(norms, mask=internal_mask)
    neighbors_norms = np.ma.masked_array(norms, mask=neighbors_mask)

    internal_matrix = settings.internal_weight * \
        (settings.nominal_dist_internal - internal_norms) ** 2
    cost += np.sum(internal_matrix.filled(0))

    neighbors_matrix = settings.neighbors_weight * \
        (settings.nominal_dist_neighbors - neighbors_norms) ** 2
    cost += np.sum(neighbors_matrix.filled(0))

    internal_grad_mask = np.repeat(internal_mask, 2, axis=np.newaxis)
    neighbors_grad_mask = np.repeat(neighbors_mask, 2, axis=np.newaxis)

    internal_grad_common = settings.internal_weight * \
        (internal_norms - settings.nominal_dist_internal) * (4 / internal_norms)
    internal_grad_matrix = deltas * internal_grad_common[:, :, None]
    grad += np.reshape(np.sum(internal_grad_matrix.filled(0), axis=1), grad.shape)

    neighbors_grad_common = settings.neighbors_weight * \
        (neighbors_norms - settings.nominal_dist_neighbors) * (4 / neighbors_norms)
    neighbors_grad_matrix = deltas * neighbors_grad_common[:, :, None]
    grad += np.reshape(np.sum(neighbors_grad_matrix.filled(0), axis=1), grad.shape)

    return (cost, grad)


def nonneighboring_distance_cost_term(x, g, node_indices, node_component_neighbors, settings):
    xr = np.reshape(x, (-1, 2))

    cost = 0
    grad = np.zeros(x.shape[0])

    nonneighbors_mask = np.identity(xr.shape[0])
    for node in g:
        i = node_indices[node]

        for neighbor in g.neighbors(node):
            j = node_indices[neighbor]
            nonneighbors_mask[i, j] = 1
            nonneighbors_mask[j, i] = 1

    deltas = xr[:, None, :] - xr[None, :, :]
    norms = np.linalg.norm(deltas, axis=2)

    nodes_to_ignore = (norms >= settings.minimum_dist_others)
    mask = np.logical_or(nonneighbors_mask, nodes_to_ignore)

    masked_norms = np.ma.masked_array(norms, mask=mask)

    cost_matrix = settings.others_weight * (settings.minimum_dist_others - masked_norms) ** 2
    cost += np.sum(cost_matrix.filled(0))

    grad_mask = np.repeat(mask, 2, axis=np.newaxis)

    grad_common_term = settings.others_weight * \
        (masked_norms - settings.minimum_dist_others) * (4 / masked_norms)
    grad_matrix = deltas * grad_common_term[:, :, None]

    grad += np.reshape(np.sum(grad_matrix.filled(0), axis=1), grad.shape)

    return (cost, grad)


def centroid_deviation_cost_term(x, g, node_indices, node_component_neighbors, settings):
    xr = np.reshape(x, (-1, 2))

    cost = 0
    grad = np.zeros(x.shape[0])

    cost_mask = np.ones((xr.shape[0], xr.shape[0], 2))
    grad_mask = np.ones((xr.shape[0], xr.shape[0], 2))
    num_neighbors = np.ones((xr.shape[0], 1))
    for node in g:
        i = node_indices[node]
        neighbors = list(g.neighbors(node))
        if len(neighbors) > 1:
            grad_mask[i, i] = 0
            num_neighbors[i] = len(neighbors)
            for neighbor in neighbors:
                j = node_indices[neighbor]
                cost_mask[i, j] = 0
                grad_mask[j, i] = 0

    deltas = xr[:, None, :] - xr[None, :, :]
    masked_deltas = np.ma.masked_array(deltas, mask=cost_mask)
    centroid_deviations = np.sum(masked_deltas, axis=1) / num_neighbors

    cost_matrix = settings.centroid_deviation_weight * centroid_deviations ** 2
    cost += np.sum(cost_matrix.filled(0))

    reshaped = np.reshape(centroid_deviations, (1, xr.shape[0], 2))
    repeated = np.repeat(reshaped, xr.shape[0], axis=0)

    grad_deviations = np.ma.masked_array(repeated, mask=grad_mask)

    grad_coefficients_diag = settings.centroid_deviation_weight * 2 * np.identity(xr.shape[0])
    grad_coefficients_off_diag = settings.centroid_deviation_weight * -2 * np.ones((xr.shape[0], xr.shape[0], 2)) / num_neighbors
    np.fill_diagonal(grad_coefficients_off_diag[:, :, 0], 0)
    np.fill_diagonal(grad_coefficients_off_diag[:, :, 1], 0)

    grad_coefficients = grad_coefficients_off_diag + grad_coefficients_diag[:, :, None]

    grad_matrix = grad_coefficients * grad_deviations
    grad += np.reshape(np.sum(grad_matrix.filled(0), axis=1), grad.shape)

    return (cost, grad)


def right_angle_deviation_cost_term(x, g, node_indices, node_component_neighbors, settings):
    xr = np.reshape(x, (-1, 2))

    cost = 0
    grad = np.zeros(x.shape[0])

    internal_mask = np.ones((xr.shape[0], xr.shape[0], 2))
    for node in g:
        i = node_indices[node]
        for neighbor in node_component_neighbors[node]:
            j = node_indices[neighbor]
            internal_mask[i, j] = 0
            internal_mask[j, i] = 0

    deltas = xr[:, None, :] - xr[None, :, :]

    internal_deltas = np.ma.masked_array(deltas, mask=internal_mask)

    dxdy = np.product(internal_deltas, axis=2)

    cost_matrix = settings.right_angle_weight * dxdy ** 2
    cost += np.sum(cost_matrix.filled(0))

    grad_common = settings.right_angle_weight * 4 * dxdy[:, :, None]
    grad_matrix = grad_common * np.flip(internal_deltas, axis=2)
    grad += np.reshape(np.sum(grad_matrix.filled(0), axis=1), grad.shape)

    return (cost, grad)


def horizontal_deviation_cost_term(x, g, node_indices, node_component_neighbors, settings):
    xr = np.reshape(x, (-1, 2))

    cost = 0
    grad = np.zeros(x.shape[0])

    internal_mask = np.ones((xr.shape[0], xr.shape[0]))
    for node in g:
        i = node_indices[node]
        for neighbor in node_component_neighbors[node]:
            j = node_indices[neighbor]
            internal_mask[i, j] = 0
            internal_mask[j, i] = 0

    delta_y = (xr[:, None, :] - xr[None, :, :])[:, :, 1]

    internal_delta_y = np.ma.masked_array(delta_y, mask=internal_mask)

    cost_matrix = settings.horizontal_weight * internal_delta_y ** 2
    cost += np.sum(cost_matrix.filled(0))

    grad_matrix = np.ma.masked_array(np.zeros((xr.shape[0], xr.shape[0], 2)))
    grad_matrix[:, :, 1] = settings.horizontal_weight * 4 * internal_delta_y
    grad += np.reshape(np.sum(grad_matrix.filled(0), axis=1), grad.shape)

    return (cost, grad)
