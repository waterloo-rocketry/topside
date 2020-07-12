import topside as top


def test_valid_file():
    file = top.File('topside/pdl/example.yaml')

    parsed = top.Parser([file])

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

    plumb = top.PlumbingEngine(
        parsed.components, parsed.mapping, parsed.initial_pressures, parsed.initial_states)

    assert plumb.is_valid()
