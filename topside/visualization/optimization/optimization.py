from dataclasses import dataclass
from functools import partial

import numpy as np
from scipy.optimize import minimize, NonlinearConstraint

import topside as top


@dataclass
class OptimizerSettings:
    nominal_dist_neighbors: float = 7
    neighbors_weight: float = 10

    nominal_dist_internal: float = 4
    internal_weight: float = 50

    minimum_dist_others: float = 10
    others_weight: float = 1

    right_angle_weight: float = 0
    horizontal_weight: float = 0

    centroid_deviation_weight: float = 15


def cost_fn(x, g, node_indices, node_component_neighbors, settings):
    c1, g1 = top.neighboring_distance_cost_term(
        x, g, node_indices, node_component_neighbors, settings)
    c2, g2 = top.nonneighboring_distance_cost_term(
        x, g, node_indices, node_component_neighbors, settings)
    c3, g3 = top.centroid_deviation_cost_term(
        x, g, node_indices, node_component_neighbors, settings)
    c4, g4 = top.right_angle_deviation_cost_term(
        x, g, node_indices, node_component_neighbors, settings)
    c5, g5 = top.horizontal_deviation_cost_term(
        x, g, node_indices, node_component_neighbors, settings)

    cost = sum([c1, c2, c3, c4, c5])
    grad = sum([g1, g2, g3, g4, g5])

    return (cost, grad)


def pos_dict_to_vector(pos, node_indices):
    a = np.zeros((len(pos) * 2, 1))
    for n, i in node_indices.items():
        a[2*i, 0] = pos[n][0]
        a[2*i+1, 0] = pos[n][1]
    return a


def vector_to_pos_dict(v, node_indices):
    if v.ndim == 1:
        v = np.reshape(v, (-1, 1))
    return {n: np.array([v[2*i, 0], v[2*i+1, 0]]) for n, i in node_indices.items()}


def make_initial_pos(num_nodes):
    # TODO(jacob): Investigate smarter initialization strategies.
    initial_pos = np.zeros((num_nodes*2, 1))
    for i in range(num_nodes):
        initial_pos[2*i] = i
        initial_pos[2*i+1] = i / 2

    return initial_pos


def layout_plumbing_engine(plumbing_engine):
    t, non_atm_nodes, components = top.terminal_graph(plumbing_engine)

    node_indices = {n: i for i, n in enumerate(t.nodes)}

    node_component_neighbors = {n: [] for n in t.nodes}
    for cname, cnodes in components.items():
        for n in cnodes:
            node_component_neighbors[n] = [v for v in t.neighbors(n) if v in cnodes]

    initial_pos = make_initial_pos(t.order())

    stage_1_settings = OptimizerSettings(horizontal_weight=0.1)
    stage_1_args = (t, node_indices, node_component_neighbors, stage_1_settings)

    # TODO(jacob): Investigate if BFGS is really the best option.
    initial_positioning_res = minimize(cost_fn, initial_pos, jac=True, method='BFGS',
                                       args=stage_1_args, options={'maxiter': 400})
    print(initial_positioning_res)

    # TODO(jacob): Reformulate this to only create one constraint that
    # covers every component instead# of having N constraints for N
    # components.
    constraints = []
    for cname, cnodes in components.items():
        i = node_indices[cnodes[0]]
        j = node_indices[cnodes[1]]

        cons_f = partial(top.right_angle_cons_f, i, j)
        cons_j = partial(top.right_angle_cons_j, i, j)
        cons_h = partial(top.right_angle_cons_h, i, j)

        cons = NonlinearConstraint(cons_f, 0, 0, jac=cons_j, hess=cons_h)

        constraints.append(cons)

    stage_2_settings = OptimizerSettings()
    stage_2_args = (t, node_indices, node_component_neighbors, stage_2_settings)

    fine_tuning_res = minimize(cost_fn, initial_positioning_res.x, jac=True, method='SLSQP',
                               constraints=constraints, args=stage_2_args,
                               options={'maxiter': 200})
    print(fine_tuning_res)

    pos = top.vector_to_pos_dict(fine_tuning_res.x, node_indices)

    return pos
