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


def make_cost_terms(g, node_indices, neighbors, settings):
    c1 = top.NeighboringDistance(g, node_indices, neighbors, settings, internal=True)
    c2 = top.NeighboringDistance(g, node_indices, neighbors, settings, internal=False)
    c3 = top.NonNeighboringDistance(g, node_indices, neighbors, settings)
    c4 = top.CentroidDeviation(g, node_indices, neighbors, settings)
    c5 = top.RightAngleDeviation(g, node_indices, neighbors, settings)
    c6 = top.HorizontalDeviation(g, node_indices, neighbors, settings)

    return [c1, c2, c3, c4, c5, c6]


def make_constraints(components, node_indices):
    # TODO(jacob): Consider reformulating this to only create one
    # constraint that covers every component instead of having N
    # constraints for N components.
    constraints = []
    for cnodes in components:
        i = node_indices[cnodes[0]]
        j = node_indices[cnodes[1]]

        cons_f = partial(top.right_angle_cons_f, i, j)
        cons_j = partial(top.right_angle_cons_j, i, j)
        cons_h = partial(top.right_angle_cons_h, i, j)

        cons = NonlinearConstraint(cons_f, 0, 0, jac=cons_j, hess=cons_h)

        constraints.append(cons)

    return constraints


def make_costargs(x):
    xr = np.reshape(x, (-1, 2))
    deltas = xr[:, None, :] - xr[None, :, :]
    norms = np.linalg.norm(deltas, axis=2)

    costargs = {
        'deltas': deltas,
        'norms': norms
    }

    return costargs


def cost_fn(x, cost_terms):
    # Pre-calculate deltas and norms to avoid repeated calculation
    # between cost terms.
    costargs = make_costargs(x)

    costs = []
    grads = []

    for ct in cost_terms:
        cost, grad = ct.evaluate(costargs)
        costs.append(cost)
        grads.append(grad)

    cost = sum(costs)
    grad = sum(grads)

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
    """
    Given a plumbing engine, determine the best placement of components.

    Parameters
    ----------

    plumbing_engine: topside.PlumbingEngine

    Returns
    -------

    pos: dict
        dict with keys corresponding to the nodes in the terminal graph
        of plumbing_engine and values corresponding to the x-y point
        that the node should be placed at.
    """
    t = top.terminal_graph(plumbing_engine)
    components = top.component_nodes(plumbing_engine)

    node_indices = {n: i for i, n in enumerate(t.nodes)}

    neighbors = {n: [] for n in t.nodes}
    for cnodes in components:
        for n in cnodes:
            neighbors[n] = [v for v in t.neighbors(n) if v in cnodes]

    initial_pos = make_initial_pos(t.order())

    stage_1_settings = OptimizerSettings(horizontal_weight=0.1)
    stage_1_cost_terms = make_cost_terms(
        t, node_indices, neighbors, stage_1_settings)
    stage_1_args = (stage_1_cost_terms)

    # TODO(jacob): Investigate if BFGS is really the best option.
    # Consider implementing the Hessian of the cost function in order
    # to try other methods (trust-exact, trust-krylov, etc.).
    initial_positioning_res = minimize(cost_fn, initial_pos, jac=True, method='BFGS',
                                       args=stage_1_args, options={'maxiter': 400})
    print(initial_positioning_res)

    constraints = make_constraints(components, node_indices)

    stage_2_settings = OptimizerSettings()
    stage_2_cost_terms = make_cost_terms(
        t, node_indices, neighbors, stage_2_settings)
    stage_2_args = (stage_2_cost_terms)

    fine_tuning_res = minimize(cost_fn, initial_positioning_res.x, jac=True, method='SLSQP',
                               constraints=constraints, args=stage_2_args,
                               options={'maxiter': 200})
    print(fine_tuning_res)

    pos = top.vector_to_pos_dict(fine_tuning_res.x, node_indices)

    return pos
