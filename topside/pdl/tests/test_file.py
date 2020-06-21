import pytest

import topside as top
import topside.pdl.exceptions as exceptions


def test_valid_PDL():
    file = top.File("topside/pdl/example.yaml")
    file.validate()

    assert file.typedefs == {"valve": ["edge1", "open_teq", "closed_teq"]}


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

    f_no_params = top.File(no_params, input_type="s")
    with pytest.raises(exceptions.BadInputError):
        f_no_params.validate()


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
    f_no_name = top.File(no_name, input_type="s")
    with pytest.raises(exceptions.BadInputError):
        f_no_name.validate()

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
    f_no_state_no_teq = top.File(no_state_no_teq, input_type="s")
    with pytest.raises(exceptions.BadInputError):
        f_no_state_no_teq.validate()

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

    f_param_missing = top.File(param_missing, input_type="s")
    with pytest.raises(exceptions.BadInputError):
        f_param_missing.validate()

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
    f_no_hoisting = top.File(no_hoisting, input_type="s")
    with pytest.raises(exceptions.BadInputError):
        f_no_hoisting.validate()


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
    f_missing_states = top.File(missing_states, "s")
    with pytest.raises(exceptions.BadInputError):
        f_missing_states.validate()

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

    f_incomplete_nodes = top.File(incomplete_nodes, "s")
    with pytest.raises(exceptions.BadInputError):
        f_incomplete_nodes.validate()
