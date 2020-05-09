import numpy as np


# TODO(jacob): Vectorize all of these for (hopefully) significant
# speedup.

def neighboring_distance_cost_term(x, g, node_indices, node_component_neighbors, settings):
    xr = np.reshape(x, (-1, 2))

    cost = 0
    grad = np.zeros(x.shape[0])

    for node in g:
        i = node_indices[node]

        for other in g:
            if other == node:
                continue

            j = node_indices[other]
            delta = xr[j] - xr[i]
            dx = delta[0]
            dy = delta[1]
            norm = np.linalg.norm(delta)

            if other in g.neighbors(node):
                if other in node_component_neighbors[node]:
                    nominal_dist = settings.nominal_dist_internal
                    weight = settings.internal_weight
                   
                else:
                    nominal_dist = settings.nominal_dist_neighbors
                    weight = settings.neighbors_weight

                cost += weight * (nominal_dist - norm) ** 2
                common = weight * -2 * (nominal_dist - norm) / norm
                grad[2*i] += common * -dx
                grad[2*i+1] += common * -dy
                grad[2*j] += common * dx
                grad[2*j+1] += common * dy

    return cost, grad


def nonneighboring_distance_cost_term(x, g, node_indices, node_component_neighbors, settings):
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
            norm = np.linalg.norm(delta)

            if other not in g.neighbors(node):
                if norm < settings.minimum_dist_others:
                    cost += settings.others_weight * (norm - settings.minimum_dist_others) ** 2
                    common = settings.others_weight * 2 * (norm - settings.minimum_dist_others) * (0.5 / norm) * 2
                    grad[2*i] += common * delta[0]
                    grad[2*i+1] += common * delta[1]
                    grad[2*j] += common * -delta[0]
                    grad[2*j+1] += common * -delta[1]
    
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
