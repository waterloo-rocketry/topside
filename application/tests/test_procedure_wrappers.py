import topside as top
from ..procedure_wrappers import ProcedureStepsModel, ProcedureConditionWrapper


def test_condition_wrapper_wraps_condition():
    cond = top.WaitFor(1)
    cond.reinitialize({'time': 0})

    wrapper = ProcedureConditionWrapper(cond, None)

    assert not wrapper.satisfied
    cond.update({'time': 101})
    assert wrapper.satisfied


def test_steps_model_no_procedure():
    model = ProcedureStepsModel()

    assert model.procedure is None
    assert model.condition_wrappers == []
    assert model.rowCount() == 0
    assert model.data(1, ProcedureStepsModel.ActionRoleIdx) is None


def test_steps_model_change_proc():
    model = ProcedureStepsModel()

    procedure = top.Procedure('main', [
        top.ProcedureStep('1', top.StateChangeAction('injector_valve', 'open'), [
            (top.Immediate(), top.Transition('main', '2'))
        ], 'PRIMARY'),
        top.ProcedureStep('2', top.StateChangeAction('vent_valve', 'closed'), [], 'SECONDARY')
    ])

    wrapper = ProcedureConditionWrapper(top.Immediate(), top.Transition('main', '2'))

    model.change_procedure(procedure)

    assert model.procedure == procedure
    assert model.condition_wrappers == [[wrapper], []]
    assert model.rowCount() == 2


def test_steps_model_get_data():
    procedure = top.Procedure('main', [
        top.ProcedureStep('1', top.StateChangeAction('injector_valve', 'open'), [
            (top.Immediate(), top.Transition('main', '2'))
        ], 'PRIMARY'),
        top.ProcedureStep('2', top.MiscAction('Approach the launch tower'), [], 'SECONDARY')
    ])

    model = ProcedureStepsModel(procedure)

    wrapper = ProcedureConditionWrapper(top.Immediate(), top.Transition('main', '2'))

    idx_0 = model.createIndex(0, 0)
    assert model.data(idx_0, ProcedureStepsModel.ActionRoleIdx) == 'Set injector_valve to open'
    assert model.data(idx_0, ProcedureStepsModel.OperatorRoleIdx) == 'PRIMARY'
    assert model.data(idx_0, ProcedureStepsModel.ConditionsRoleIdx) == [wrapper]

    idx_1 = model.createIndex(1, 0)
    assert model.data(idx_1, ProcedureStepsModel.ActionRoleIdx) == 'Approach the launch tower'
    assert model.data(idx_1, ProcedureStepsModel.OperatorRoleIdx) == 'SECONDARY'
    assert model.data(idx_1, ProcedureStepsModel.ConditionsRoleIdx) == []
