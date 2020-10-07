from dataclasses import dataclass


@dataclass(frozen=True)
class PlumbingInvalidReason:
    error_message: str


@dataclass(frozen=True)
class InvalidComponentName(PlumbingInvalidReason):
    component_name: str


@dataclass(frozen=True)
class InvalidStateName(PlumbingInvalidReason):
    component_name: str
    state_id: str


@dataclass(frozen=True)
class InvalidComponentNode(PlumbingInvalidReason):
    component_name: str
    node_name: str


@dataclass(frozen=True)
class InvalidComponentEdge(PlumbingInvalidReason):
    edge: tuple


@dataclass(frozen=True)
class InvalidNodePressure(PlumbingInvalidReason):
    node_name: str


@dataclass(frozen=True)
class InvalidTeq(PlumbingInvalidReason):
    component_name: str
    state_id: str
    edge_id: tuple
    teq: int


@dataclass(frozen=True)
class DuplicateError(PlumbingInvalidReason):
    original_error: PlumbingInvalidReason


def multi_error_msg(error_msg):
    message = "Multiple instances of this error were detected:\n"\
        + error_msg + "\n"\
        + "Consider checking for errors in the mapping dict."
    return message


def add_error(error, error_set):
    if error in error_set:
        error = DuplicateError(multi_error_msg(error.error_message), error)
    error_set.add(error)
