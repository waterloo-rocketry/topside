import os

import pytest

import topside as top


def test_parse_one_step():
    proclang = '''
    main:
        1. set injector_valve to open
    '''
    suite = top.proclang.parse(proclang)

    expected_suite = top.ProcedureSuite([
        top.Procedure('main', [
            top.ProcedureStep('1', top.Action('injector_valve', 'open'), [])
        ])
    ])

    assert suite == expected_suite


def test_parse_two_steps():
    proclang = '''
    main:
        1. set injector_valve to open
        2. set vent_valve to closed
    '''
    suite = top.proclang.parse(proclang)

    expected_suite = top.ProcedureSuite([
        top.Procedure('main', [
            top.ProcedureStep('1', top.Action('injector_valve', 'open'), [
                (top.Immediate(), top.Transition('main', '2'))
            ]),
            top.ProcedureStep('2', top.Action('vent_valve', 'closed'), [])
        ])
    ])

    assert suite == expected_suite


def test_parse_two_procedures():
    proclang = '''
    main:
        1. set injector_valve to open
        2. set vent_valve to closed

    abort:
        1. set injector_valve to closed
        2. set vent_valve to open
    '''
    suite = top.proclang.parse(proclang)

    expected_suite = top.ProcedureSuite([
        top.Procedure('main', [
            top.ProcedureStep('1', top.Action('injector_valve', 'open'), [
                (top.Immediate(), top.Transition('main', '2'))
            ]),
            top.ProcedureStep('2', top.Action('vent_valve', 'closed'), [])
        ]),
        top.Procedure('abort', [
            top.ProcedureStep('1', top.Action('injector_valve', 'closed'), [
                (top.Immediate(), top.Transition('abort', '2'))
            ]),
            top.ProcedureStep('2', top.Action('vent_valve', 'open'), [])
        ])
    ])

    assert suite == expected_suite


def test_parse_step_with_waituntil():
    proclang = '''
    main:
        1. set injector_valve to open
        2. [10s] set vent_valve to closed
    '''
    suite = top.proclang.parse(proclang)

    expected_suite = top.ProcedureSuite([
        top.Procedure('main', [
            top.ProcedureStep('1', top.Action('injector_valve', 'open'), [
                (top.WaitUntil(10e6), top.Transition('main', '2'))
            ]),
            top.ProcedureStep('2', top.Action('vent_valve', 'closed'), [])
        ])
    ])

    assert suite == expected_suite


def test_parse_steps_with_comparisons():
    proclang = '''
    main:
        1. set injector_valve to open
        2. [p1 < 100] set vent_valve to closed
        3. [p1 > 100] set vent_valve to open
        4. [p1 <= 100] set vent_valve to closed
        5. [p1 >= 100] set vent_valve to open
        6. [p1 == 100] set vent_valve to closed
    '''
    suite = top.proclang.parse(proclang)

    expected_suite = top.ProcedureSuite([
        top.Procedure('main', [
            top.ProcedureStep('1', top.Action('injector_valve', 'open'), [
                (top.Less('p1', 100), top.Transition('main', '2'))
            ]),
            top.ProcedureStep('2', top.Action('vent_valve', 'closed'), [
                (top.Greater('p1', 100), top.Transition('main', '3'))
            ]),
            top.ProcedureStep('3', top.Action('vent_valve', 'open'), [
                (top.LessEqual('p1', 100), top.Transition('main', '4'))
            ]),
            top.ProcedureStep('4', top.Action('vent_valve', 'closed'), [
                (top.GreaterEqual('p1', 100), top.Transition('main', '5'))
            ]),
            top.ProcedureStep('5', top.Action('vent_valve', 'open'), [
                (top.Equal('p1', 100), top.Transition('main', '6'))
            ]),
            top.ProcedureStep('6', top.Action('vent_valve', 'closed'), [])
        ])
    ])

    assert suite == expected_suite


def test_parse_step_with_one_deviation():
    proclang = '''
    main:
        1. set injector_valve to open
            - [p1 < 500] abort.1
        2. set vent_valve to closed
    '''
    suite = top.proclang.parse(proclang)

    expected_suite = top.ProcedureSuite([
        top.Procedure('main', [
            top.ProcedureStep('1', top.Action('injector_valve', 'open'), [
                (top.Less('p1', 500), top.Transition('abort', '1')),
                (top.Immediate(), top.Transition('main', '2'))
            ]),
            top.ProcedureStep('2', top.Action('vent_valve', 'closed'), [])
        ])
    ])

    assert suite == expected_suite


def test_parse_step_with_two_deviations():
    proclang = '''
    main:
        1. set injector_valve to open
            - [p1 < 500] abort.1
            - [300s] abort.2
        2. set vent_valve to closed
    '''
    suite = top.proclang.parse(proclang)

    expected_suite = top.ProcedureSuite([
        top.Procedure('main', [
            top.ProcedureStep('1', top.Action('injector_valve', 'open'), [
                (top.Less('p1', 500), top.Transition('abort', '1')),
                (top.WaitUntil(300e6), top.Transition('abort', '2')),
                (top.Immediate(), top.Transition('main', '2'))
            ]),
            top.ProcedureStep('2', top.Action('vent_valve', 'closed'), [])
        ])
    ])

    assert suite == expected_suite


def test_whitespace_is_irrelevant():
    proclang = '''
    main: 1. set injector_valve to open
    - [p1    <    500] abort.1
    - [300 s] abort.2
    2. 
    set vent_valve to closed
    '''
    suite = top.proclang.parse(proclang)

    expected_suite = top.ProcedureSuite([
        top.Procedure('main', [
            top.ProcedureStep('1', top.Action('injector_valve', 'open'), [
                (top.Less('p1', 500), top.Transition('abort', '1')),
                (top.WaitUntil(300e6), top.Transition('abort', '2')),
                (top.Immediate(), top.Transition('main', '2'))
            ]),
            top.ProcedureStep('2', top.Action('vent_valve', 'closed'), [])
        ])
    ])

    assert suite == expected_suite


def test_steps_without_procedure_throws():
    proclang = '''
    1. set injector_valve to open
    2. set vent_valve to closed
    '''
    with pytest.raises(Exception):
        top.proclang.parse(proclang)


def test_duplicate_step_id_throws():
    proclang = '''
    main:
        1. set injector_valve to open
        1. set vent_valve to closed
    '''
    with pytest.raises(Exception):
        top.proclang.parse(proclang)


def test_duplicate_procedure_name_throws():
    proclang = '''
    main:
        1. set injector_valve to open
        2. set vent_valve to closed

    main:
        1. set injector_valve to closed
        2. set vent_valve to open
    '''
    with pytest.raises(Exception):
        top.proclang.parse(proclang)


def test_parse_from_file():
    filepath = os.path.join(os.path.dirname(__file__), 'example.proc')
    suite = top.proclang.parse_from_file(filepath)

    expected_suite = top.ProcedureSuite([
        top.Procedure('main', [
            top.ProcedureStep('1', top.Action('series_fill_valve', 'closed'), [
                (top.WaitUntil(5e6), top.Transition('main', '2'))
            ]),
            top.ProcedureStep('2', top.Action('supply_valve', 'open'), [
                (top.Less('p1', 600), top.Transition('abort_1', '1')),
                (top.Greater('p1', 1000), top.Transition('abort_2', '1')),
                (top.Immediate(), top.Transition('main', '3'))
            ]),
            top.ProcedureStep('3', top.Action('series_fill_valve', 'open'), [
                (top.Immediate(), top.Transition('main', '4'))
            ]),
            top.ProcedureStep('4', top.Action('remote_fill_valve', 'open'), [
                (top.WaitUntil(180e6), top.Transition('main', '5'))
            ]),
            top.ProcedureStep('5', top.Action('remote_fill_valve', 'closed'), [
                (top.Immediate(), top.Transition('main', '6'))
            ]),
            top.ProcedureStep('6', top.Action('remote_vent_valve', 'open'), [])
        ]),
        top.Procedure('abort_1', [
            top.ProcedureStep('1', top.Action('supply_valve', 'closed'), [
                (top.WaitUntil(10e6), top.Transition('abort_1', '2'))
            ]),
            top.ProcedureStep('2', top.Action('remote_vent_valve', 'open'), [])
        ]),
        top.Procedure('abort_2', [
            top.ProcedureStep('1', top.Action('supply_valve', 'closed'), [
                (top.Immediate(), top.Transition('abort_2', '2'))
            ]),
            top.ProcedureStep('2', top.Action('line_vent_valve', 'open'), [])
        ]),
    ])

    assert suite == expected_suite
