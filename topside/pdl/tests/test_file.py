import textwrap

import pytest

import topside as top
import topside.pdl.exceptions as exceptions
import topside.pdl.utils as utils


def test_valid_pdl():
    file = top.File(utils.example_path)

    assert file.namespace == 'example'
    assert file.imports == ['stdlib']

    assert len(file.typedefs) == 2
    assert len(file.components) == 6
    assert len(file.graphs) == 2


def test_no_import():
    no_import = textwrap.dedent("""\
    name: example
    body:
    - typedef:
        params: [edge_name, open_teq, closed_teq]
        name: valve
        edges:
          edge1:
            nodes: [0, 1]
        states:
          open:
            edge1: open_teq
          closed:
            edge1: closed_teq
    """)
    file = top.File(no_import, 's')

    assert file.namespace == 'example'
    assert file.imports == []

    assert len(file.typedefs) == 1


def test_invalid_typedef():
    no_params = textwrap.dedent("""\
    name: example
    import: [stdlib]
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
    """)

    with pytest.raises(exceptions.BadInputError):
        _ = top.File(no_params, input_type='s')


def test_invalid_no_component_name():
    no_name = textwrap.dedent("""\
    name: example
    import: [stdlib]
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
    """)
    with pytest.raises(exceptions.BadInputError):
        _ = top.File(no_name, input_type='s')


def test_invalid_no_state_no_teq():

    no_state_no_teq = textwrap.dedent("""\
    name: example
    import: [stdlib]
    body:
    - component:
        name: vent_plug
        edges:
          edge1:
            nodes: [0, 1]
    """)
    with pytest.raises(exceptions.BadInputError):
        _ = top.File(no_state_no_teq, input_type='s')


def test_invalid_param_missing():
    param_missing = textwrap.dedent("""\
    name: example
    import: [stdlib]
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
    """)
    with pytest.raises(exceptions.BadInputError):
        _ = top.File(param_missing, input_type='s')


def test_invalid_no_hoisting():
    no_hoisting = textwrap.dedent("""\
    name: example
    import: [stdlib]
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
    """)
    with pytest.raises(exceptions.BadInputError):
        _ = top.File(no_hoisting, input_type='s')


def test_invalid_incomplete_node():
    # A is missing its components
    incomplete_nodes = textwrap.dedent("""\
    name: example
    import: [stdlib]
    body:
    - graph:
        name: main
        nodes:
          A:
            fixed_pressure: 500

          B:
            components:
              - [fill_valve, 1]

        states:
          fill_valve: closed
          vent_valve: open
          three_way_valve: left
    """)

    with pytest.raises(exceptions.BadInputError):
        _ = top.File(incomplete_nodes, 's')


def test_bad_input_type():
    bad_format = 'p'
    with pytest.raises(exceptions.BadInputError) as err:
        _ = top.File("", bad_format)

    assert "invalid input type" in str(err)


def test_bad_entry():
    nonexistent = 'parameter'

    bad_entry = textwrap.dedent(f"""\
    name: example
    import: [stdlib]
    body:
    - {nonexistent}:
        name: a

    - graph:
        name: main
        nodes:
          A:
            fixed_pressure: 500

          B:
            components:
              - [fill_valve, 1]

        states:
          fill_valve: closed
          vent_valve: open
          three_way_valve: left
        """)

    with pytest.raises(exceptions.BadInputError) as err:
        _ = top.File(bad_entry, 's')

    assert "invalid input type" in str(err)


def test_invalid_param():
    not_param = 'nonexistent'

    invalid_param = textwrap.dedent(f"""\
    name: example
    import: [stdlib]
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
          edge1: fav_edge
          open_teq: 1
          {not_param}: closed
    """)

    with pytest.raises(exceptions.BadInputError) as err:
        _ = top.File(invalid_param, 's')

    assert "not found" in str(err)


def test_bad_check_entry():
    with pytest.raises(exceptions.BadInputError) as err:
        top.check_fields(None, [])

    assert "empty entry" in str(err)
