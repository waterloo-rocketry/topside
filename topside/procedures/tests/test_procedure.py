import pytest

import topside as top


def test_procedure_builds_steps():
    s1 = top.ProcedureStep('s1', None, {})
    s2 = top.ProcedureStep('s2', None, {})
    s3 = top.ProcedureStep('s3', None, {})

    proc = top.Procedure('p1', [s1, s2, s3])

    assert proc.steps == {'s1': s1, 's2': s2, 's3': s3}


def test_procedure_step_list():
    s1 = top.ProcedureStep('s1', None, {})
    s2 = top.ProcedureStep('s2', None, {})
    s3 = top.ProcedureStep('s3', None, {})

    proc = top.Procedure('p1', [s1, s2, s3])

    assert proc.step_list == [s1, s2, s3]


def test_procedure_duplicate_id_errors():
    s1 = top.ProcedureStep('s1', None, {})
    s2 = top.ProcedureStep('s2', None, {})
    s3 = top.ProcedureStep('s1', None, {})

    with pytest.raises(ValueError):
        top.Procedure('p1', [s1, s2, s3])


def test_procedure_index_of():
    s1 = top.ProcedureStep('s1', None, {})
    s2 = top.ProcedureStep('s2', None, {})
    s3 = top.ProcedureStep('s3', None, {})

    proc = top.Procedure('p1', [s1, s2, s3])

    assert proc.index_of('s1') == 0
    assert proc.index_of('s2') == 1
    assert proc.index_of('s3') == 2
