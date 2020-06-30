import pytest

import topside as top
import topside.pdl.exceptions as exceptions


def test_valid_pdl():
    file = top.File("topside/pdl/example.yaml")

    assert file.namespace == "potato"
    assert file.imports == ["stdlib"]

    assert len(file.typedefs) == 1
    assert len(file.components) == 6
    assert len(file.graphs) == 1


def test_invalid_typedef():
    no_params =\
        """
name: potato
import: [stdlib, other_lib]
body:
- typedef:
    params:
    name: valve
    edges:
      edge1:
        nodes: [0, 1]
    states:
      open:
        edge1: open_teq
      closed:
        edge1: closed_teq
"""

    with pytest.raises(exceptions.BadInputError):
        _ = top.File(no_params, input_type="s")


def test_invalid_component():
    no_name =\
        """
name: potato
import: [stdlib, other_lib]
body:
- component:
    edges:
      edge1:
        nodes: [0, 1]
    states:
      open:
        edge1: 1
      closed:
        edge1: closed
"""
    with pytest.raises(exceptions.BadInputError):
        _ = top.File(no_name, input_type="s")

    no_state_no_teq =\
        """
name: potato
import: [stdlib, other_lib]
body:
- component:
    name: vent_plug
    edges:
      edge1:
        nodes: [0, 1]
"""
    with pytest.raises(exceptions.BadInputError):
        _ = top.File(no_state_no_teq, input_type="s")

    param_missing =\
        """
name: potato
import: [stdlib, other_lib]
body:
- typedef:
    params: [edge1, open_teq, closed_teq]
    name: valve
    edges:
      edge1:
        nodes: [0, 1]
    states:
      open:
        edge1: open_teq
      closed:
        edge1: closed_teq
- component:
    name: vent_valve
    type: valve
    params:
      open_teq: 1
      closed_teq: closed
"""

    with pytest.raises(exceptions.BadInputError):
        _ = top.File(param_missing, input_type="s")

    no_hoisting =\
        """
name: potato
import: [stdlib, other_lib]
body:
- component:
    name: vent_valve
    type: valve
    params:
      edge1: fav_edge
      open_teq: 1
      closed_teq: closed
- typedef:
    params: [edge1, open_teq, closed_teq]
    name: valve
    edges:
      edge1:
        nodes: [0, 1]
    states:
      open:
        edge1: open_teq
      closed:
        edge1: closed_teq
"""
    with pytest.raises(exceptions.BadInputError):
        _ = top.File(no_hoisting, input_type="s")


def test_invalid_graph():
    missing_states =\
        """
name: potato
import: [stdlib, other_lib]
body:
- graph:
    name: main
    nodes:
      A:
        fixed_pressure: 500
        components:
          - [fill_valve, 0]

      B:
        components:
          - [fill_valve, 1]
          - [vent_valve, 0]
          - [check_valve, 0]

      C:
        initial_pressure: 10
        components:
          - [check_valve, 1]
          - [three_way_valve, 0]

      D:
        components:
          - [three_way_valve, 1]
          - [vent_plug, 0]

      atm:
        components:
          - [three_way_valve, 2]
          - [vent_plug, 1]
          - [vent_valve, 1]
"""
    with pytest.raises(exceptions.BadInputError):
        _ = top.File(missing_states, "s")

    incomplete_nodes =\
        """
name: potato
import: [stdlib, other_lib]
body:
- graph:
    name: main
    nodes:
      A:
        fixed_pressure: 500

      B:
        components:
          - [fill_valve, 1]
          - [vent_valve, 0]
          - [check_valve, 0]

      C:
        initial_pressure: 10
        components:
          - [check_valve, 1]
          - [three_way_valve, 0]

      D:
        components:
          - [three_way_valve, 1]
          - [vent_plug, 0]

      atm:
        components:
          - [three_way_valve, 2]
          - [vent_plug, 1]
          - [vent_valve, 1]

    states:
      fill_valve: closed
      vent_valve: open
      three_way_valve: left
"""

    with pytest.raises(exceptions.BadInputError):
        _ = top.File(incomplete_nodes, "s")
