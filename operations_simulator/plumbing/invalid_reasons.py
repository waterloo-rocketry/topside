from dataclasses import dataclass
from typing import Tuple


@dataclass
class PlumbingInvalidReason:
    error_message: str


@dataclass
class InvalidComponentName(PlumbingInvalidReason):
    component_name: str


@dataclass
class InvalidStateName(PlumbingInvalidReason):
    component_name: str
    state_id: str


@dataclass
class InvalidComponentNode(PlumbingInvalidReason):
    component_name: str
    node_name: str


@dataclass
class InvalidNodePressure(PlumbingInvalidReason):
    node_name: str


@dataclass
class InvalidTeq(PlumbingInvalidReason):
    component_name: str
    state_id: str
    edge_id: Tuple
    teq: int
