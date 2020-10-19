import textwrap

import pytest

import topside as top
import topside.pdl.exceptions as exceptions
import topside.pdl.utils as utils


def test_valid_file():

    parsed = top.Parser([utils.example_path])

    assert len(parsed.components) == 6
    for component in parsed.components.values():
        assert component.is_valid()

    assert parsed.initial_pressures == {
        'A': (500, True),
        'C': (10, False)
    }

    assert parsed.initial_states == {
        'fill_valve': 'closed',
        'vent_valve': 'open',
        'three_way_valve': 'left',
        'hole_valve': 'open',
        'vent_plug': 'default',
        'check_valve': 'default'
    }

    assert parsed.mapping == {
        'fill_valve': {
            0: 'A',
            1: 'B'
        },
        'vent_valve': {
            0: 'B',
            1: 'atm'
        },
        'three_way_valve': {
            0: 'C',
            1: 'D',
            2: 'atm'
        },
        'hole_valve': {
            0: 'D',
            1: 'E'
        },
        'vent_plug': {
            0: 'D',
            1: 'atm'
        },
        'check_valve': {
            0: 'B',
            1: 'C',
        }
    }

    for component in parsed.components.values():
        assert component.is_valid()

    plumb = parsed.make_engine()

    assert plumb.is_valid()

    assert len(plumb.nodes()) == 6
    assert set(plumb.nodes(data=False)) == {'A', 'B', 'C', 'D', 'E', 'atm'}

    assert plumb.current_state() == parsed.initial_states
    assert plumb.current_pressures() == {
        'A': 500,
        'B': 0,
        'C': 10,
        'D': 0,
        'E': 0,
        'atm': 0
    }


def test_single_file():
    parsed = top.Parser(utils.example_path)

    # results should be identical to the above, just check that it loaded
    # in at all.
    assert len(parsed.components) == 6


def test_invalid_main():
    not_main = "NOT_MAIN"
    no_main_graph = textwrap.dedent(f"""\
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
        name: {not_main}
        nodes:
          A:
            fixed_pressure: 500
            components:
              - [fill_valve, 0]

          B:
            components:
              - [fill_valve, 1]
        states:
          fill_valve: open
    """)
    with pytest.raises(exceptions.BadInputError) as err:
        top.Parser([no_main_graph], 's')
    assert "graph main" in str(err)


def test_invalid_component():
    low_teq = 1e-9
    teq_too_low = textwrap.dedent(f"""\
    name: example
    body:
    - component:
        name: fill_valve
        edges:
          edge1:
            nodes: [0, 1]
        states:
          open:
            edge1: {low_teq}
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
        states:
          fill_valve: open
    """)

    # this shouldn't raise an error, invalid components are legal
    parse = top.Parser([teq_too_low], 's')

    plumb = parse.make_engine()
    assert not plumb.is_valid()


def test_standard_extract_edges():
    standard_entry = {
        'name': 'example',
        'edges': {
            'edge1': {
                'nodes': [0, 1]
            },
            'edge2': {
                'nodes': [1, 2]
            }
        }
    }

    extracted_standard_entry = top.extract_edges(standard_entry)
    assert extracted_standard_entry == {
        'edge1': (
            (0, 1, 'fwd'),
            (1, 0, 'back')
        ),
        'edge2': (
            (1, 2, 'fwd'),
            (2, 1, 'back')
        )
    }


def test_extract_repeated_edges():
    repeated_entry = {
        'name': 'example',
        'edges': {
            'edge1': {
                'nodes': [0, 1]
            },
            'edge2': {
                'nodes': [1, 0]
            }
        }
    }

    extracted_repeat_entry = top.extract_edges(repeated_entry)
    assert extracted_repeat_entry == {
        'edge1': (
            (0, 1, 'fwd'),
            (1, 0, 'back')
        ),
        'edge2': (
            (1, 0, 'fwd2'),
            (0, 1, 'back2')
        )
    }


def test_invalid_extract_edges():
    too_many_nodes = {
        'name': 'example',
        'edges': {
            'edge1': {
                'nodes': [0, 1, 2]
            },
            'edge2': {
                'nodes': [1, 0]
            }
        }
    }

    with pytest.raises(exceptions.BadInputError) as err:
        top.extract_edges(too_many_nodes)
    assert "malformed nodes" in str(err)


def test_load_iterables():
    file_1 = textwrap.dedent("""\
    name: file1
    body:
    - component:
        name: fill_valve
        edges:
          edge1:
            nodes: [0, 1]
        states:
          open:
            edge1: 1
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
        states:
          fill_valve: open
    """)

    file_2 = textwrap.dedent("""\
    name: file2
    body:
    - component:
        name: check_valve
        edges:
          edge1:
            nodes: [0, 1]
        states:
          open:
            edge1: 1
          closed:
            edge1: closed
    - graph:
        name: main
        nodes:
          C:
            fixed_pressure: 500
            components:
              - [check_valve, 0]

          D:
            components:
              - [check_valve, 1]
        states:
          check_valve: open
    """)

    parse_list = top.Parser([file_1, file_2], 's')
    parse_tuple = top.Parser((file_1, file_2), 's')
    parse_dict = top.Parser({file_1: True, file_2: True}, 's')

    assert len(parse_list.components) == 2
    assert len(parse_tuple.components) == 2
    assert len(parse_dict.components) == 2
