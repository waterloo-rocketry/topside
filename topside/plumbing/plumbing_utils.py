DEFAULT_TIME_RESOLUTION_MICROS = 10000
DEFAULT_RESOLUTION_SCALE = 20
MIN_TIME_RES_MICROS = 1
TEQ_MIN = MIN_TIME_RES_MICROS * DEFAULT_RESOLUTION_SCALE
FC_MAX = 4.5 / TEQ_MIN
CLOSED_KEYWORD = 'closed'

#TODO(wendi): provide functions for querying these min/max values


def teq_to_FC(teq):
    if teq == 0:
        fc = FC_MAX
    elif teq == CLOSED_KEYWORD:
        fc = 0
    else:
        fc = 4.5 / teq
    return fc


def FC_to_teq(FC):
    if FC == 0:
        return CLOSED_KEYWORD
    else:
        return 4.5 / FC


def micros_to_s(micros):
    return micros / 1e6


def s_to_micros(sec):
    return sec * 1e6


def flatten(args, unpack_tuples=True):
    """Take list of lists and/or tuples and flatten it to a one dimensional list."""
    flattened_args = []
    for arg in args:
        unpack = isinstance(arg, (list, tuple)) if unpack_tuples else isinstance(arg, list)
        if unpack:
            flattened_args.extend(arg)
        else:
            flattened_args.append(arg)

    return flattened_args


def converged(p1, p2, d_t, eps):
    return abs(p2 - p1) / micros_to_s(d_t) < eps


def all_converged(all_states, d_t, eps):
    if len(all_states) < 2:
        return False
    for node in all_states[0].keys():
        p1 = all_states[-1][node]
        p2 = all_states[-2][node]
        if not converged(p1, p2, d_t, eps):
            return False

    return True
