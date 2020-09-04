import pytest

import topside as top


def test_procedure_builds_steps():
    s1 = top.ProcedureStep('s1', None, [])
    s2 = top.ProcedureStep('s2', None, [])
    s3 = top.ProcedureStep('s3', None, [])

    proc = top.Procedure('p1', [s1, s2, s3])

    assert proc.steps == {'s1': s1, 's2': s2, 's3': s3}


def test_procedure_step_list():
    s1 = top.ProcedureStep('s1', None, [])
    s2 = top.ProcedureStep('s2', None, [])
    s3 = top.ProcedureStep('s3', None, [])

    proc = top.Procedure('p1', [s1, s2, s3])

    assert proc.step_list == [s1, s2, s3]


def test_procedure_duplicate_id_errors():
    s1 = top.ProcedureStep('s1', None, [])
    s2 = top.ProcedureStep('s2', None, [])
    s3 = top.ProcedureStep('s1', None, [])

    with pytest.raises(ValueError):
        top.Procedure('p1', [s1, s2, s3])


def test_procedure_index_of():
    s1 = top.ProcedureStep('s1', None, [])
    s2 = top.ProcedureStep('s2', None, [])
    s3 = top.ProcedureStep('s3', None, [])

    proc = top.Procedure('p1', [s1, s2, s3])

    assert proc.index_of('s1') == 0
    assert proc.index_of('s2') == 1
    assert proc.index_of('s3') == 2


def test_procedure_equality_equal():
    s1 = top.ProcedureStep('s1', None, [])
    s2 = top.ProcedureStep('s2', None, [])
    s3 = top.ProcedureStep('s3', None, [])

    proc_1 = top.Procedure('p1', [s1, s2, s3])
    proc_2 = top.Procedure('p1', [s1, s2, s3])

    assert proc_1 == proc_2


def test_procedure_equality_different_id():
    s1 = top.ProcedureStep('s1', None, [])
    s2 = top.ProcedureStep('s2', None, [])
    s3 = top.ProcedureStep('s3', None, [])

    proc_1 = top.Procedure('p1', [s1, s2, s3])
    proc_2 = top.Procedure('p2', [s1, s2, s3])

    assert proc_1 != proc_2


def test_procedure_equality_different_steps():
    s1 = top.ProcedureStep('s1', None, [])
    s2 = top.ProcedureStep('s2', None, [])
    s3 = top.ProcedureStep('s3', None, [])

    proc_1 = top.Procedure('p1', [s1, s2])
    proc_2 = top.Procedure('p1', [s1, s3])

    assert proc_1 != proc_2


def test_procedure_suite_builds_list():
    s1 = top.ProcedureStep('s1', None, [])
    s2 = top.ProcedureStep('s2', None, [])
    s3 = top.ProcedureStep('s3', None, [])

    proc_1 = top.Procedure('p1', [s1, s2])
    proc_2 = top.Procedure('p2', [s1, s3])

    suite = top.ProcedureSuite([proc_1, proc_2])

    assert suite.procedures == {'p1': proc_1, 'p2': proc_2}


def test_procedure_suite_sets_starting_procedure():
    suite = top.ProcedureSuite([], 'not_main')
    assert suite.starting_procedure_id == 'not_main'


def test_procedure_suite_defaults_to_main():
    suite = top.ProcedureSuite([])
    assert suite.starting_procedure_id == 'main'


def test_procedure_suite_duplicate_name_errors():
    s1 = top.ProcedureStep('s1', None, [])
    s2 = top.ProcedureStep('s2', None, [])
    s3 = top.ProcedureStep('s3', None, [])

    proc_1 = top.Procedure('p1', [s1, s2])
    proc_2 = top.Procedure('p1', [s1, s3])

    with pytest.raises(Exception):
        top.ProcedureSuite([proc_1, proc_2])


def test_procedure_suite_equality_equal():
    s1 = top.ProcedureStep('s1', None, [])
    s2 = top.ProcedureStep('s2', None, [])
    s3 = top.ProcedureStep('s3', None, [])

    proc_1 = top.Procedure('p1', [s1, s2])
    proc_2 = top.Procedure('p2', [s1, s3])

    suite_1 = top.ProcedureSuite([proc_1, proc_2], 'p1')
    suite_2 = top.ProcedureSuite([proc_1, proc_2], 'p1')

    assert suite_1 == suite_2


def test_procedure_suite_equality_order_irrelevant():
    s1 = top.ProcedureStep('s1', None, [])
    s2 = top.ProcedureStep('s2', None, [])
    s3 = top.ProcedureStep('s3', None, [])

    proc_1 = top.Procedure('p1', [s1, s2])
    proc_2 = top.Procedure('p2', [s1, s3])

    suite_1 = top.ProcedureSuite([proc_1, proc_2], 'p1')
    suite_2 = top.ProcedureSuite([proc_2, proc_1], 'p1')

    assert suite_1 == suite_2


def test_procedure_suite_equality_different_starting_procedure():
    s1 = top.ProcedureStep('s1', None, [])
    s2 = top.ProcedureStep('s2', None, [])
    s3 = top.ProcedureStep('s3', None, [])

    proc_1 = top.Procedure('p1', [s1, s2])
    proc_2 = top.Procedure('p2', [s1, s3])

    suite_1 = top.ProcedureSuite([proc_1, proc_2], 'p1')
    suite_2 = top.ProcedureSuite([proc_1, proc_2], 'p2')

    assert suite_1 != suite_2


def test_procedure_suite_equality_different_procedures():
    s1 = top.ProcedureStep('s1', None, [])
    s2 = top.ProcedureStep('s2', None, [])
    s3 = top.ProcedureStep('s3', None, [])

    proc_1 = top.Procedure('p1', [s1, s2])
    proc_2 = top.Procedure('p2', [s1, s3])

    suite_1 = top.ProcedureSuite([proc_1], 'p1')
    suite_2 = top.ProcedureSuite([proc_1, proc_2], 'p1')

    assert suite_1 != suite_2


def test_procedure_suite_indexing():
    s1 = top.ProcedureStep('s1', None, [])
    s2 = top.ProcedureStep('s2', None, [])
    s3 = top.ProcedureStep('s3', None, [])

    proc_1 = top.Procedure('p1', [s1, s2])
    proc_2 = top.Procedure('p2', [s1, s3])

    suite = top.ProcedureSuite([proc_1, proc_2])

    assert suite['p1'] == proc_1
