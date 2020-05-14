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

    for node in g:
        i = node_indices[node]

        nb_coords = np.array([xr[node_indices[nb]] for nb in g.neighbors(node)])
        num_nb = len(nb_coords)

        if num_nb > 1:
            nb_centroid = np.sum(nb_coords, axis=0) / num_nb

            cent_diff_x = xr[i, 0] - nb_centroid[0]
            cent_diff_y = xr[i, 1] - nb_centroid[1]

            cost += settings.centroid_deviation_weight * cent_diff_x ** 2
            grad[2*i] += settings.centroid_deviation_weight * 2 * cent_diff_x

            cost += settings.centroid_deviation_weight * cent_diff_y ** 2
            grad[2*i+1] += settings.centroid_deviation_weight * 2 * cent_diff_y

            for nb in g.neighbors(node):
                j = node_indices[nb]
                grad[2*j] += settings.centroid_deviation_weight * (-2 / num_nb) * cent_diff_x
                grad[2*j+1] += settings.centroid_deviation_weight * (-2 / num_nb) * cent_diff_y

    return (cost, grad)


def right_angle_deviation_cost_term(x, g, node_indices, node_component_neighbors, settings):
    xr = np.reshape(x, (-1, 2))

    cost = 0
    grad = np.zeros(x.shape[0])

    for node in g:
        i = node_indices[node]

        for other in g:
            if other == node:
                continue

            j = node_indices[other]
            delta = xr[i] - xr[j]
            dx = delta[0]
            dy = delta[1]

            if other in node_component_neighbors[node]:
                cost += settings.right_angle_weight * (dx * dy) ** 2
                grad[2*i] += settings.right_angle_weight * 2 * dy**2 * dx
                grad[2*i+1] += settings.right_angle_weight * 2 * dy * dx**2
                grad[2*j] += settings.right_angle_weight * -2 * dy**2 * dx
                grad[2*j+1] += settings.right_angle_weight * -2 * dy * dx**2

    return (cost, grad)


def horizontal_deviation_cost_term(x, g, node_indices, node_component_neighbors, settings):
    xr = np.reshape(x, (-1, 2))

    cost = 0
    grad = np.zeros(x.shape[0])

    for node in g:
        i = node_indices[node]

        for other in g:
            if other == node:
                continue

            j = node_indices[other]
            delta = xr[i] - xr[j]
            dx = delta[0]
            dy = delta[1]

            if other in node_component_neighbors[node]:
                cost += settings.horizontal_weight * dy ** 2
                grad[2*i+1] += settings.horizontal_weight * 2 * dy
                grad[2*j+1] += settings.horizontal_weight * -2 * dy

    return (cost, grad)
