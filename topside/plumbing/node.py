from abc import ABC, abstractmethod
import networkx as nx

import topside.plumbing.plumbing_utils as utils


def instantiate_node(type_id=None):
    ret = None
    if type_id == utils.ATM:
        ret = AtmNode()
    else:
        ret = GenericNode()
    return ret


class Node(ABC):
    """
    Abstract base class for all nodes.

    Should never be used directly, so we tag all its methods as abstract.
    """
    @abstractmethod
    def update_pressure(self, new_pressure, **kwargs):
        pass

    @abstractmethod
    def get_pressure(self):
        pass

    @abstractmethod
    def update_fixed(self, fixed):
        pass

    @abstractmethod
    def get_fixed(self):
        pass


class GenericNode(Node):
    def __init__(self, pressure=0, fixed=False):
        """Instantiate a generic node."""
        self.__pressure = pressure
        self.fixed = fixed

    def __str__(self):
        return f'[GenericNode] pressure: {self.__pressure}, fixed: {self.fixed}'

    def update_pressure(self, new_pressure, **kwargs):
        self.__pressure = new_pressure

    def get_pressure(self):
        return self.__pressure

    def update_fixed(self, fixed):
        self.fixed = fixed

    def get_fixed(self):
        return self.fixed

    def __eq__(self, other):
        return isinstance(other, GenericNode) and \
            self.__pressure == other.__pressure and \
            self.fixed == other.fixed


class AtmNode(Node):
    def __str__(self):
        return f'[AtmNode] pressure: 0, fixed: True'

    def update_pressure(self, new_pressure, **kwargs):
        pass

    def get_pressure(self):
        return 0

    def update_fixed(self, fixed):
        pass

    def get_fixed(self):
        return True

    def __eq__(self, other):
        return isinstance(other, AtmNode)
