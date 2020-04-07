DEFAULT_TIME_RESOLUTION_MICROS = 10000
DEFAULT_RESOLUTION_SCALE = 20
TEQ_MIN = 1 * DEFAULT_RESOLUTION_SCALE
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
        return 'closed'
    else:
        return 4.5 / FC
