import numpy as np


def right_angle_cons_f(i, j, x):
    return (x[2*i] - x[2*j]) * (x[2*i+1] - x[2*j+1])


def right_angle_cons_j(i, j, x):
    grad = np.zeros((1, len(x)))

    ix = 2*i
    iy = 2*i+1
    jx = 2*j
    jy = 2*j+1

    dx = x[ix] - x[jx]
    dy = x[iy] - x[jy]

    grad[0, ix] = dy
    grad[0, iy] = dx
    grad[0, jx] = -dy
    grad[0, jy] = -dx

    return grad


# NOTE(jacob): The optimization method we're using right now doesn't
# use the Hessian of the constraint, but we still implement it so that
# we can easily switch optimization methods if desired.
def right_angle_cons_h(i, j, x, v):
    hess = np.zeros((len(x), len(x)))

    ix = 2*i
    iy = 2*i+1
    jx = 2*j
    jy = 2*j+1
    
    hess[ix, iy] = 1
    hess[iy, ix] = 1

    hess[ix, jy] = -1
    hess[jy, ix] = -1
    
    hess[jx, iy] = -1
    hess[iy, jx] = -1
    
    hess[jx, jy] = 1
    hess[jy, jx] = 1

    return hess
