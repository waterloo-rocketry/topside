import pytest

import topside as top
import topside.pdl.exceptions as exceptions


def test_package_storage():
    file = top.File('topside/pdl/example.yaml')

    pack = top.Package([file])

    namespace = file.namespace
    assert len(pack.typedefs) == 2
    assert 'example' in pack.typedefs and 'stdlib' in pack.typedefs

    assert len(pack.component_dict[namespace]) == 6
    assert len(pack.component_dict['stdlib']) == 0
    assert len(pack.components()) == 6

    assert len(pack.typedefs[namespace]) == 1
    assert len(pack.typedefs['stdlib']) == 1

    assert len(pack.graph_dict[namespace]) == 2
    assert len(pack.graph_dict['stdlib']) == 0
    assert len(pack.graphs()) == 2


def test_package_typedefs():
    file = top.File('topside/pdl/example.yaml')
    namespace = file.namespace

    pack = top.Package([file])

    var_open = 'open_teq'
    var_closed = 'closed_teq'
    var_name = 'edge_name'

    for component in pack.component_dict[namespace]:
        # ensure typedef fulfillment occurred
        assert 'type' not in component and 'params' not in component
        assert 'edges' in component

        # ensure variables were replaced
        if component['name'] == 'vent_valve':
            assert var_name not in list(component['edges'].keys())
            assert var_open not in component['states']['open']
            assert var_closed not in component['states']['closed']

        if component['name'] == 'hole':
            assert var_name not in list(component['edges'].keys())
            assert var_open not in component['states']['open']


def test_package_shortcuts():
    file = top.File('topside/pdl/example.yaml')
    namespace = file.namespace

    pack = top.Package([file])
    for component in pack.component_dict[namespace]:
        assert 'states' in component
        for edges in component['states'].values():
            for teq in edges.values():
                assert 'fwd' in teq and 'back' in teq


def test_files_unchanged():
    file = top.File('topside/pdl/example.yaml')

    top.Package([file])

    assert len(file.typedefs) == 1
    assert len(file.components) == 6
    assert len(file.graphs) == 2


def test_invalid_import():
    bad_import = "NONEXISTENT"
    invalid_import =\
        f"""
name: example
import: [stdlib, {bad_import}]
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
"""
    invalid_import_file = top.File(invalid_import, input_type='s')
    with pytest.raises(exceptions.BadInputError):
        top.Package([invalid_import_file])


def test_invalid_bad_import_type():
    # typedef not found errors having to do with imported files will only be caught at the package
    # level, not at the file one. We can look at changing this if we change the implementation of
    # how importable files are stored.
    bad_type = "NONEXISTENT_TYPE"
    bad_imported_type =\
        f"""
name: example
import: [stdlib]
body:
- component:
    name: vent_valve
    type: stdlib.{bad_type}
    params:
      edge_name: fav_edge
      open_teq: 5
      closed_teq: closed
"""
    bad_imported_type_file = top.File(bad_imported_type, input_type='s')
    with pytest.raises(exceptions.BadInputError):
        top.Package([bad_imported_type_file])


def test_invalid_empty_package():
    with pytest.raises(exceptions.BadInputError):
        top.Package([])


def test_invalid_nested_import():
    nested_import =\
        """
name: example
import: [stdlib]
body:
- component:
    name: vent_valve
    type: stdlib.NEST.hole
    params:
      edge_name: fav_edge
      open_teq: 5
"""
    nested_import_file = top.File(nested_import, input_type='s')
    with pytest.raises(NotImplementedError):
        top.Package([nested_import_file])


def test_duplicate_names():
    file_1 =\
        """
name: name1
body:
- component:
    name: fill_valve
    edges:
      edge1:
        nodes: [0, 1]
    states:
      open:
        edge1: 6
      closed:
        edge1: closed
"""

    file_2 =\
        """
name: name2
body:
- component:
    name: fill_valve
    edges:
      edge1:
        nodes: [0, 1]
    states:
      open:
        edge1: 6
      closed:
        edge1: closed
"""
    duplicate_pack = top.Package([top.File(file_1, 's'), top.File(file_2, 's')])
    assert duplicate_pack.component_dict["name1"][0]['name'] == "name1.fill_valve"
    assert duplicate_pack.component_dict["name2"][0]['name'] == "name2.fill_valve"


def test_invalid_graph_missing_states():
    missing_states =\
        """
name: example
import: [stdlib]
body:
- component:
    name: fill_valve
    edges:
      edge1:
        nodes: [0, 1]
    states:
      open:
        edge1: 6
      closed:
        edge1: closed
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
"""
    missing_states_file = top.File(missing_states, 's')
    with pytest.raises(exceptions.BadInputError):
        top.Package([missing_states_file])
