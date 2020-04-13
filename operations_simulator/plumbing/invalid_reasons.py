from dataclasses import dataclass
from typing import Tuple


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
class InvalidNodePressure(PlumbingInvalidReason):
    node_name: str


@dataclass(frozen=True)
class InvalidTeq(PlumbingInvalidReason):
    component_name: str
    state_id: str
    edge_id: Tuple
    teq: int
