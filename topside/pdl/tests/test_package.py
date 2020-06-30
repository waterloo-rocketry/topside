import pytest

import topside as top
import topside.pdl.exceptions as exceptions


def test_package_storage():
    file = top.File("topside/pdl/example.yaml")

    pack = top.Package([file])

    namespace = file.namespace
    assert len(pack.typedefs) == 2
    assert "potato" in pack.typedefs and "stdlib" in pack.typedefs

    assert len(pack.components[namespace]) == 6
    assert len(pack.components["stdlib"]) == 0

    assert len(pack.typedefs[namespace]) == 1
    assert len(pack.typedefs["stdlib"]) == 1

    assert len(pack.graphs[namespace]) == 1
    assert len(pack.graphs["stdlib"]) == 0


def test_package_typedefs():
    file = top.File("topside/pdl/example.yaml")
    namespace = file.namespace

    pack = top.Package([file])

    var_open = "open_teq"
    var_closed = "closed_teq"
    var_name = "edge_name"

    for component in pack.components[namespace]:
        # ensure typedef fulfillment occurred
        assert "type" not in component and "params" not in component
        assert "edges" in component

        # ensure variables were replaced
        if component["name"] == "vent_valve":
            assert var_name not in list(component["edges"].keys())
            assert var_open not in component["states"]["open"]
            assert var_closed not in component["states"]["closed"]

        if component["name"] == "hole":
            assert var_name not in list(component["edges"].keys())
            assert var_open not in component["states"]["open"]


def test_package_shortcuts():
    file = top.File("topside/pdl/example.yaml")
    namespace = file.namespace

    pack = top.Package([file])
    for component in pack.components[namespace]:
        assert "states" in component
        for edges in component["states"].values():
            for teq in edges.values():
                assert "fwd" in teq and "back" in teq


def test_files_unchanged():
    file = top.File("topside/pdl/example.yaml")

    _ = top.Package([file])

    assert len(file.typedefs) == 1
    assert len(file.components) == 6
    assert len(file.graphs) == 1


def test_errors():
    invalid_import =\
        """
name: potato
import: [stdlib, NONEXISTENT]
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
    invalid_import_file = top.File(invalid_import, input_type="s")
    with pytest.raises(exceptions.BadInputError):
        _ = top.Package([invalid_import_file])


    # typedef not found errors having to do with imported files will only be caught at the package
    # level, not at the file one. We can look at changing this if we change the implementation of
    # how importable files are stored.
    bad_imported_type =\
        """
name: potato
import: [stdlib]
body:
- component:
    name: vent_valve
    type: stdlib.NONEXISTENT_TYPE
    params:
      edge_name: fav_edge
      open_teq: 5
      closed_teq: closed
"""
    bad_imported_type_file = top.File(bad_imported_type, input_type="s")
    with pytest.raises(exceptions.BadInputError):
        _ = top.Package([bad_imported_type_file])
