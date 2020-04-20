DEFAULT_TIME_RESOLUTION_MICROS = 10000
DEFAULT_RESOLUTION_SCALE = 20
MIN_TIME_RES_MICROS = 1
TEQ_MIN = MIN_TIME_RES_MICROS * DEFAULT_RESOLUTION_SCALE
FC_MAX = 4.5 / TEQ_MIN
CLOSED_KEYWORD = 'closed'


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


def flatten(args, allow_tuples=True):
    flattened_args = []
    for arg in args:
        unpack = isinstance(arg, (list, tuple)) if allow_tuples else isinstance(arg, list)
        if unpack:
            flattened_args.extend(arg)
        else:
            flattened_args.append(arg)

    return flattened_args
