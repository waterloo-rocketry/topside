import os

import pytest

import topside as top


def test_parse_one_step():
    proclang = '''
    main:
        1. PRIMARY: set injector_valve to open
    '''
    suite = top.proclang.parse(proclang)

    expected_suite = top.ProcedureSuite([
        top.Procedure('main', [
            top.ProcedureStep('1', top.StateChangeAction('injector_valve', 'open'), [], 'PRIMARY')
        ])
    ])

    assert suite == expected_suite


def test_parse_two_steps():
    proclang = '''
    main:
        1. PRIMARY: set injector_valve to open
        2. PRIMARY: set vent_valve to closed
    '''
    suite = top.proclang.parse(proclang)

    expected_suite = top.ProcedureSuite([
        top.Procedure('main', [
            top.ProcedureStep('1', top.StateChangeAction('injector_valve', 'open'), [
                (top.Immediate(), top.Transition('main', '2'))
            ], 'PRIMARY'),
            top.ProcedureStep('2', top.StateChangeAction('vent_valve', 'closed'), [], 'PRIMARY')
        ])
    ])

    assert suite == expected_suite


def test_set_case_insensitive():
    proclang = '''
    main:
        1. PRIMARY: Set injector_valve to open
        2. PRIMARY: set injector_valve to open
    '''
    suite = top.proclang.parse(proclang)

    expected_suite = top.ProcedureSuite([
        top.Procedure('main', [
            top.ProcedureStep('1', top.StateChangeAction('injector_valve', 'open'), [
                (top.Immediate(), top.Transition('main', '2'))
            ], 'PRIMARY'),
            top.ProcedureStep('2', top.StateChangeAction('injector_valve', 'open'), [], 'PRIMARY')
        ])
    ])

    assert suite == expected_suite


def test_different_step_ids():
    proclang = '''
    main:
        1. PRIMARY: Set injector_valve to open
        10. PRIMARY: Set injector_valve to open
        100. PRIMARY: Set injector_valve to open
        a. PRIMARY: Set injector_valve to open
        ab. PRIMARY: Set injector_valve to open
        a1. PRIMARY: Set injector_valve to open
        1a. PRIMARY: Set injector_valve to open
        a_1. PRIMARY: Set injector_valve to open
        1_a. PRIMARY: Set injector_valve to open
    '''
    suite = top.proclang.parse(proclang)

    expected_suite = top.ProcedureSuite([
        top.Procedure('main', [
            top.ProcedureStep('1', top.StateChangeAction('injector_valve', 'open'), [
                (top.Immediate(), top.Transition('main', '10'))
            ], 'PRIMARY'),
            top.ProcedureStep('10', top.StateChangeAction('injector_valve', 'open'), [
                (top.Immediate(), top.Transition('main', '100'))
            ], 'PRIMARY'),
            top.ProcedureStep('100', top.StateChangeAction('injector_valve', 'open'), [
                (top.Immediate(), top.Transition('main', 'a'))
            ], 'PRIMARY'),
            top.ProcedureStep('a', top.StateChangeAction('injector_valve', 'open'), [
                (top.Immediate(), top.Transition('main', 'ab'))
            ], 'PRIMARY'),
            top.ProcedureStep('ab', top.StateChangeAction('injector_valve', 'open'), [
                (top.Immediate(), top.Transition('main', 'a1'))
            ], 'PRIMARY'),
            top.ProcedureStep('a1', top.StateChangeAction('injector_valve', 'open'), [
                (top.Immediate(), top.Transition('main', '1a'))
            ], 'PRIMARY'),
            top.ProcedureStep('1a', top.StateChangeAction('injector_valve', 'open'), [
                (top.Immediate(), top.Transition('main', 'a_1'))
            ], 'PRIMARY'),
            top.ProcedureStep('a_1', top.StateChangeAction('injector_valve', 'open'), [
                (top.Immediate(), top.Transition('main', '1_a'))
            ], 'PRIMARY'),
            top.ProcedureStep('1_a', top.StateChangeAction('injector_valve', 'open'), [], 'PRIMARY')
        ])
    ])

    assert suite == expected_suite


def test_parse_two_procedures():
    proclang = '''
    main:
        1. PRIMARY: set injector_valve to open
        2. PRIMARY: set vent_valve to closed

    abort:
        1. PRIMARY: set injector_valve to closed
        2. PRIMARY: set vent_valve to open
    '''
    suite = top.proclang.parse(proclang)

    expected_suite = top.ProcedureSuite([
        top.Procedure('main', [
            top.ProcedureStep('1', top.StateChangeAction('injector_valve', 'open'), [
                (top.Immediate(), top.Transition('main', '2'))
            ], 'PRIMARY'),
            top.ProcedureStep('2', top.StateChangeAction('vent_valve', 'closed'), [], 'PRIMARY')
        ]),
        top.Procedure('abort', [
            top.ProcedureStep('1', top.StateChangeAction('injector_valve', 'closed'), [
                (top.Immediate(), top.Transition('abort', '2'))
            ], 'PRIMARY'),
            top.ProcedureStep('2', top.StateChangeAction('vent_valve', 'open'), [], 'PRIMARY')
        ])
    ])

    assert suite == expected_suite


def test_parse_step_with_waituntil():
    proclang = '''
    main:
        1. PRIMARY: set injector_valve to open
        2. PRIMARY: [10s] set vent_valve to closed
    '''
    suite = top.proclang.parse(proclang)

    expected_suite = top.ProcedureSuite([
        top.Procedure('main', [
            top.ProcedureStep('1', top.StateChangeAction('injector_valve', 'open'), [
                (top.WaitUntil(10e6), top.Transition('main', '2'))
            ], 'PRIMARY'),
            top.ProcedureStep('2', top.StateChangeAction('vent_valve', 'closed'), [], 'PRIMARY')
        ])
    ])

    assert suite == expected_suite


def test_parse_steps_with_comparisons():
    proclang = '''
    main:
        1. PRIMARY: set injector_valve to open
        2. PRIMARY: [p1 < 100] set vent_valve to closed
        3. PRIMARY: [p1 > 100] set vent_valve to open
        4. PRIMARY: [p1 <= 100] set vent_valve to closed
        5. SECONDARY: [p1 >= 100] set vent_valve to open
        6. SECONDARY: [p1 == 100] set vent_valve to closed
    '''
    suite = top.proclang.parse(proclang)

    expected_suite = top.ProcedureSuite([
        top.Procedure('main', [
            top.ProcedureStep('1', top.StateChangeAction('injector_valve', 'open'), [
                (top.Less('p1', 100), top.Transition('main', '2'))
            ], 'PRIMARY'),
            top.ProcedureStep('2', top.StateChangeAction('vent_valve', 'closed'), [
                (top.Greater('p1', 100), top.Transition('main', '3'))
            ], 'PRIMARY'),
            top.ProcedureStep('3', top.StateChangeAction('vent_valve', 'open'), [
                (top.LessEqual('p1', 100), top.Transition('main', '4'))
            ], 'PRIMARY'),
            top.ProcedureStep('4', top.StateChangeAction('vent_valve', 'closed'), [
                (top.GreaterEqual('p1', 100), top.Transition('main', '5'))
            ], 'PRIMARY'),
            top.ProcedureStep('5', top.StateChangeAction('vent_valve', 'open'), [
                (top.Equal('p1', 100), top.Transition('main', '6'))
            ], 'SECONDARY'),
            top.ProcedureStep('6', top.StateChangeAction('vent_valve', 'closed'), [], 'SECONDARY')
        ])
    ])

    assert suite == expected_suite


def test_parse_step_with_one_deviation():
    proclang = '''
    main:
        1. PRIMARY: set injector_valve to open
            - [p1 < 500] abort.1
        2. PRIMARY: set vent_valve to closed
    '''
    suite = top.proclang.parse(proclang)

    expected_suite = top.ProcedureSuite([
        top.Procedure('main', [
            top.ProcedureStep('1', top.StateChangeAction('injector_valve', 'open'), [
                (top.Less('p1', 500), top.Transition('abort', '1')),
                (top.Immediate(), top.Transition('main', '2'))
            ], 'PRIMARY'),
            top.ProcedureStep('2', top.StateChangeAction('vent_valve', 'closed'), [], 'PRIMARY')
        ])
    ])

    assert suite == expected_suite


def test_parse_step_with_two_deviations():
    proclang = '''
    main:
        1. PRIMARY: set injector_valve to open
            - [p1 < 500] abort.1
            - [300s] abort.2
        2. PRIMARY: set vent_valve to closed
    '''
    suite = top.proclang.parse(proclang)

    expected_suite = top.ProcedureSuite([
        top.Procedure('main', [
            top.ProcedureStep('1', top.StateChangeAction('injector_valve', 'open'), [
                (top.Less('p1', 500), top.Transition('abort', '1')),
                (top.WaitUntil(300e6), top.Transition('abort', '2')),
                (top.Immediate(), top.Transition('main', '2'))
            ], 'PRIMARY'),
            top.ProcedureStep('2', top.StateChangeAction('vent_valve', 'closed'), [], 'PRIMARY')
        ])
    ])

    assert suite == expected_suite


def test_whitespace_is_irrelevant():
    proclang = '''
    main: 1. CONTROL: set injector_valve to open
    - [p1    <    500] abort.1
    - [300 s] abort.2
    2. CONTROL:
    set vent_valve to closed
    '''
    suite = top.proclang.parse(proclang)

    expected_suite = top.ProcedureSuite([
        top.Procedure('main', [
            top.ProcedureStep('1', top.StateChangeAction('injector_valve', 'open'), [
                (top.Less('p1', 500), top.Transition('abort', '1')),
                (top.WaitUntil(300e6), top.Transition('abort', '2')),
                (top.Immediate(), top.Transition('main', '2'))
            ], 'CONTROL'),
            top.ProcedureStep('2', top.StateChangeAction('vent_valve', 'closed'), [], 'CONTROL')
        ])
    ])

    assert suite == expected_suite


def test_steps_without_procedure_throws():
    proclang = '''
    1. PRIMARY: set injector_valve to open
    2. PRIMARY: set vent_valve to closed
    '''
    with pytest.raises(Exception):
        top.proclang.parse(proclang)


def test_duplicate_step_id_throws():
    proclang = '''
    main:
        1. PRIMARY: set injector_valve to open
        1. PRIMARY: set vent_valve to closed
    '''
    with pytest.raises(Exception):
        top.proclang.parse(proclang)


def test_duplicate_procedure_name_throws():
    proclang = '''
    main:
        1. PRIMARY: set injector_valve to open
        2. PRIMARY: set vent_valve to closed

    main:
        1. PRIMARY: set injector_valve to closed
        2. PRIMARY: set vent_valve to open
    '''
    with pytest.raises(Exception):
        top.proclang.parse(proclang)


def test_no_personnel_throws():
    proclang = '''
    main:
        1. set injector_valve to open
        2. set vent_valve to closed
    '''
    with pytest.raises(Exception):
        top.proclang.parse(proclang)


def test_parse_from_file():
    filepath = os.path.join(os.path.dirname(__file__), 'example.proc')
    suite = top.proclang.parse_from_file(filepath)

    expected_suite = top.ProcedureSuite([
        top.Procedure('main', [
            top.ProcedureStep('1', top.StateChangeAction('series_fill_valve', 'closed'), [
                (top.WaitUntil(5e6), top.Transition('main', '2'))
            ], 'PRIMARY'),
            top.ProcedureStep('2', top.StateChangeAction('supply_valve', 'open'), [
                (top.Less('p1', 600), top.Transition('abort_1', '1')),
                (top.Greater('p1', 1000), top.Transition('abort_2', '1')),
                (top.Immediate(), top.Transition('main', '3'))
            ], 'PRIMARY'),
            top.ProcedureStep('3', top.StateChangeAction('series_fill_valve', 'open'), [
                (top.Immediate(), top.Transition('main', '4'))
            ], 'PRIMARY'),
            top.ProcedureStep('4', top.StateChangeAction('remote_fill_valve', 'open'), [
                (top.WaitUntil(180e6), top.Transition('main', '5'))
            ], 'PRIMARY'),
            top.ProcedureStep('5', top.StateChangeAction('remote_fill_valve', 'closed'), [
                (top.Immediate(), top.Transition('main', '6'))
            ], 'PRIMARY'),
            top.ProcedureStep('6', top.StateChangeAction('remote_vent_valve', 'open'), [
                (top.Immediate(), top.Transition('main', '7'))
            ], 'PRIMARY'),
            top.ProcedureStep('7', top.MiscAction('Proceed with teardown'), [], 'OPS')
        ]),
        top.Procedure('abort_1', [
            top.ProcedureStep('1', top.StateChangeAction('supply_valve', 'closed'), [
                (top.WaitUntil(10e6), top.Transition('abort_1', '2'))
            ], 'SECONDARY'),
            top.ProcedureStep('2', top.StateChangeAction('remote_vent_valve', 'open'), [
                (top.Immediate(), top.Transition('abort_1', '3'))
            ], 'SECONDARY'),
            top.ProcedureStep('3', top.MiscAction('Proceed with teardown'), [], 'OPS')
        ]),
        top.Procedure('abort_2', [
            top.ProcedureStep('1', top.StateChangeAction('supply_valve', 'closed'), [
                (top.Immediate(), top.Transition('abort_2', '2'))
            ], 'CONTROL'),
            top.ProcedureStep('2', top.StateChangeAction('line_vent_valve', 'open'), [
                (top.Immediate(), top.Transition('abort_2', '3'))
            ], 'CONTROL'),
            top.ProcedureStep('3', top.MiscAction('Proceed with teardown'), [], 'OPS')
        ]),
    ])

    assert suite == expected_suite


def test_parse_steps_with_complex_comparisons():
    proclang = '''
    main:
        1. PRIMARY: set injector_valve to open
        2. PRIMARY: [p1 < 100 and p2 > 200] set vent_valve to closed
        3. SECONDARY: [p1 > 100 or  p2 < 200] set vent_valve to open
        4. SECONDARY: [(p1 <= 100)] set vent_valve to closed
        5. OPS: [p1 < 100 or p2 > 200 and p3 < 100] set vent_valve to open
        6. OPS: [p1 < 100 and p2 > 200 or p3 < 100] set vent_valve to open
        7. OPS: [(p1 < 100 or p2 > 200) and p3 < 100] set vent_valve to closed
    '''
    suite = top.proclang.parse(proclang)

    comp_and = top.And([top.Less('p1', 100), top.Greater('p2', 200)])
    comp_or = top.Or([top.Greater('p1', 100), top.Less('p2', 200)])
    comp_and_or_1 = top.Or([top.Less('p1', 100), top.And(
        [top.Greater('p2', 200), top.Less('p3', 100)])])
    comp_and_or_2 = top.Or(
        [top.And([top.Less('p1', 100), top.Greater('p2', 200)]), top.Less('p3', 100)])
    comp_and_or_3 = top.And(
        [top.Or([top.Less('p1', 100), top.Greater('p2', 200)]), top.Less('p3', 100)])

    expected_suite = top.ProcedureSuite([
        top.Procedure('main', [
            top.ProcedureStep('1', top.StateChangeAction('injector_valve', 'open'), [
                (comp_and, top.Transition('main', '2'))
            ], 'PRIMARY'),
            top.ProcedureStep('2', top.StateChangeAction('vent_valve', 'closed'), [
                (comp_or, top.Transition('main', '3'))
            ], 'PRIMARY'),
            top.ProcedureStep('3', top.StateChangeAction('vent_valve', 'open'), [
                (top.LessEqual('p1', 100), top.Transition('main', '4'))
            ], 'SECONDARY'),
            top.ProcedureStep('4', top.StateChangeAction('vent_valve', 'closed'), [
                (comp_and_or_1, top.Transition('main', '5'))
            ], 'SECONDARY'),
            top.ProcedureStep('5', top.StateChangeAction('vent_valve', 'open'), [
                (comp_and_or_2, top.Transition('main', '6'))
            ], 'OPS'),
            top.ProcedureStep('6', top.StateChangeAction('vent_valve', 'open'), [
                (comp_and_or_3, top.Transition('main', '7'))
            ], 'OPS'),
            top.ProcedureStep('7', top.StateChangeAction('vent_valve', 'closed'), [], 'OPS')
        ])
    ])

    assert suite == expected_suite


def test_parse_steps_with_multiple_comparisons():
    proclang = '''
    main:
        1. PRIMARY: set injector_valve to open
        2. PRIMARY: [p1 < 100 and p2 < 100 and p3 < 100] set vent_valve to closed
        3. PRIMARY: [p1 < 100 or  p2 < 100 or  p3 < 100] set vent_valve to open
        4. PRIMARY: [p1 < 100 and p2 < 100 and p3 < 100 or p1 < 100 and p2 < 100] set vent_valve to open
    '''
    suite = top.proclang.parse(proclang)

    p1 = top.Less('p1', 100)
    p2 = top.Less('p2', 100)
    p3 = top.Less('p3', 100)

    expected_suite = top.ProcedureSuite([
        top.Procedure('main', [
            top.ProcedureStep('1', top.StateChangeAction('injector_valve', 'open'), [
                (top.And([p1, p2, p3]), top.Transition('main', '2'))
            ], 'PRIMARY'),
            top.ProcedureStep('2', top.StateChangeAction('vent_valve', 'closed'), [
                (top.Or([p1, p2, p3]), top.Transition('main', '3'))
            ], 'PRIMARY'),
            top.ProcedureStep('3', top.StateChangeAction('vent_valve', 'open'), [
                (top.Or([top.And([p1, p2, p3]), top.And([p1, p2])]), top.Transition('main', '4'))
            ], 'PRIMARY'),
            top.ProcedureStep('4', top.StateChangeAction('vent_valve', 'open'), [], 'PRIMARY')
        ])
    ])

    assert suite == expected_suite


def test_parse_logical_operator_forms():
    proclang = '''
    main:
        1. PRIMARY: set injector_valve to open
        2. PRIMARY: [p1 < 100 and p2 < 100] set vent_valve to open
        3. PRIMARY: [p1 < 100 AND p2 < 100] set vent_valve to open
        4. PRIMARY: [p1 < 100 &&  p2 < 100] set vent_valve to open
        5. CONTROL: [p1 < 100 or  p2 < 100] set vent_valve to open
        6. CONTROL: [p1 < 100 OR  p2 < 100] set vent_valve to open
        7. CONTROL: [p1 < 100 ||  p2 < 100] set vent_valve to open
    '''
    suite = top.proclang.parse(proclang)

    comp_and = top.And([top.Less('p1', 100), top.Less('p2', 100)])
    comp_or = top.Or([top.Less('p1', 100), top.Less('p2', 100)])

    expected_suite = top.ProcedureSuite([
        top.Procedure('main', [
            top.ProcedureStep('1', top.StateChangeAction('injector_valve', 'open'), [
                (comp_and, top.Transition('main', '2'))
            ], 'PRIMARY'),
            top.ProcedureStep('2', top.StateChangeAction('vent_valve', 'open'), [
                (comp_and, top.Transition('main', '3'))
            ], 'PRIMARY'),
            top.ProcedureStep('3', top.StateChangeAction('vent_valve', 'open'), [
                (comp_and, top.Transition('main', '4'))
            ], 'PRIMARY'),
            top.ProcedureStep('4', top.StateChangeAction('vent_valve', 'open'), [
                (comp_or, top.Transition('main', '5'))
            ], 'PRIMARY'),
            top.ProcedureStep('5', top.StateChangeAction('vent_valve', 'open'), [
                (comp_or, top.Transition('main', '6'))
            ], 'CONTROL'),
            top.ProcedureStep('6', top.StateChangeAction('vent_valve', 'open'), [
                (comp_or, top.Transition('main', '7'))
            ], 'CONTROL'),
            top.ProcedureStep('7', top.StateChangeAction('vent_valve', 'open'), [], 'CONTROL')
        ])
    ])

    assert suite == expected_suite


def test_parse_combined_conditions():
    proclang = '''
    main:
        1. PRIMARY: set s to v
        2. PRIMARY: [p1 < 100 or 500s and p2 < 200] set s to v
    '''

    suite = top.proclang.parse(proclang)

    comp_or = top.Or([top.Less('p1', 100), top.And([top.WaitUntil(1e6*500), top.Less('p2', 200)])])
    expected_suite = top.ProcedureSuite([
        top.Procedure('main', [
            top.ProcedureStep('1', top.StateChangeAction('s', 'v'), [
                (comp_or, top.Transition('main', '2'))
            ], 'PRIMARY'),
            top.ProcedureStep('2', top.StateChangeAction('s', 'v'), [], 'PRIMARY')
        ])
    ])

    assert suite == expected_suite


def test_parse_misc_actions():
    proclang = '''
    main:
        1. CONTROL: Set injector_valve to open
        2. CONTROL: [p1 < 10] Disarm the remote control system
        3. PRIMARY: Approach the launch tower, disconnect the cylinder, and replace the cap
        4. OPS: [60s] Proceed with teardown
    '''
    suite = top.proclang.parse(proclang)

    expected_suite = top.ProcedureSuite([
        top.Procedure('main', [
            top.ProcedureStep('1', top.StateChangeAction('injector_valve', 'open'), [
                (top.Less('p1', 10), top.Transition('main', '2'))
            ], 'CONTROL'),
            top.ProcedureStep('2', top.MiscAction('Disarm the remote control system'), [
                (top.Immediate(), top.Transition('main', '3'))
            ], 'CONTROL'),
            top.ProcedureStep('3', top.MiscAction(
                'Approach the launch tower, disconnect the cylinder, and replace the cap'), [
                (top.WaitUntil(60e6), top.Transition('main', '4'))
            ], 'PRIMARY'),
            top.ProcedureStep('4', top.MiscAction('Proceed with teardown'), [], 'OPS')
        ])
    ])

    assert suite == expected_suite


def test_parse_names_with_hyphens():
    proclang = '''
    main:
        1. PRIMARY: set A-200 to open
        2. PRIMARY: set vent-valve to closed
        3. BOB-THE-BUILDER: set K-5-B to open
        4. CONTROL: set C-AB-2 to closed
        5. OPS: set A-200 to semi-closed
    '''
    suite = top.proclang.parse(proclang)

    expected_suite = top.ProcedureSuite([
        top.Procedure('main', [
            top.ProcedureStep('1', top.StateChangeAction('A-200', 'open'), [
                (top.Immediate(), top.Transition('main', '2'))
            ], 'PRIMARY'),
            top.ProcedureStep('2', top.StateChangeAction('vent-valve', 'closed'), [
                (top.Immediate(), top.Transition('main', '3'))
            ], 'PRIMARY'),
            top.ProcedureStep('3', top.StateChangeAction('K-5-B', 'open'), [
                (top.Immediate(), top.Transition('main', '4'))
            ], 'BOB-THE-BUILDER'),
            top.ProcedureStep('4', top.StateChangeAction('C-AB-2', 'closed'), [
                (top.Immediate(), top.Transition('main', '5'))
            ], 'CONTROL'),
            top.ProcedureStep('5', top.StateChangeAction('A-200', 'semi-closed'), [], 'OPS')
        ])
    ])

    assert suite == expected_suite