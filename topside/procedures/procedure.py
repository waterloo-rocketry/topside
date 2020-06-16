from dataclasses import dataclass


# TODO(jacob): Consider if any of the classes in this file could simply
# be NamedTuples instead.

@dataclass
class Action:
    """
    A state change for a single component in the plumbing engine.

    Members
    =======

    component: str
        The identifier of the component whose state will be changed.
        If part of a procedure that will be executed, this must refer to
        a valid component in the managed PlumbingEngine.

    state: str
        The state that the component will be set to. If part of a
        procedure that will be executed, this must refer to a valid
        state of `component`.
    """
    component: str
    state: str


@dataclass
class Transition:
    """
    A transition between two states in the procedure graph.

    Members
    =======

    procedure: str
        The identifier of the procedure that the next step belongs to.

    step: str
        The identifier for the next procedure step.
    """
    procedure: str
    step: str


@dataclass
class ProcedureStep:
    """
    A discrete state in the procedure graph.

    Members
    =======

    step_id: str
        An identifier for this procedure step. Expected to be unique
        within the same procedure.

    action: topside.Action
        The action that should be executed when this step is performed.

    conditions: dict
        A dict mapping topside.Condition objects to Transition objects.
        Each entry in `conditions` represents a conditional transition
        from this ProcedureStep to another step, potentially in a
        different proceddure. This dict is expected to be ordered in
        terms of condition priority; if multiple conditions are
        satisfied, the first one will be selected.
    """
    step_id: str
    action: Action
    conditions: dict


@dataclass
class Procedure:
    """
    A discrete state in the procedure graph.

    Members
    =======

    procedure_id: str
        An identifier for this procedure. Expected to be unique within
        a given procedure suite.

    steps: dict
        A dict mapping step identifier strings to ProcedureStep objects.
        This dict is expected to be ordered from first step to last
        step.
    """
    procedure_id: str
    steps: dict
