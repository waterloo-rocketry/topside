import pytest

import topside as top

def test_StateChangeAction_string():
    Action = top.StateChangeAction("component", "state")
    assert str(Action) == "myStateChangeAction: comp:component, state:state"

def test_MiscAction_string():
    Action = top.MiscAction("action_type")
    assert str(Action) == "myMiscAction: action_type:action_type"

def test_Transition_string():
    trans = top.Transition("procedure", "step")
    assert str(trans) == "myTransition: procedure:procedure, step:step"

def test_ProcedureStep_string():
    proc_step = top.ProcedureStep("step_id", top.Action(), [], "operator")
    assert str(proc_step) == "myProcedureStep: step_id:step_id, operator:operator"

def test_Procedure_string():
    proc = top.Procedure("procedure_id", [])
    assert str(proc) == "myProcedure: procedure_id:procedure_id"

def test_ProcedureSuite_string():
    proc_suite = top.ProcedureSuite([top.Procedure("procedure_id", [])], "procedure_id")
    assert str(proc_suite) == "myProcedureSuite: starting_procedure_id:procedure_id"


