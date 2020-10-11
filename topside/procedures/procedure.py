from dataclasses import dataclass

@dataclass
class Action:
    """
    A state change for a single component in the plumbing engine.

    Members
    -------

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

    def __str__(self):
        return f"""Component: {self.component}  State: {self.state}"""

@dataclass
class Transition:
    """
    A transition between two states in the procedure graph.

    Members
    -------

    procedure: str
        The identifier of the procedure that the next step belongs to.

    step: str
        The identifier for the next procedure step.
    """
    procedure: str
    step: str

    def __str__(self):
        return f"""Procedure: {self.procedure}  Step: {self.step}"""

@dataclass
class ProcedureStep:
    """
    A discrete state in the procedure graph.

    Members
    -------

    step_id: str
        An identifier for this procedure step. Expected to be unique
        within the same procedure.

    action: topside.Action
        The action that should be executed when this step is performed.

    conditions: dict
        A dict mapping topside.Condition objects to Transition objects.
        Each entry in `conditions` represents a conditional transition
        from this ProcedureStep to another step, potentially in a
        different procedure. This dict is expected to be ordered in
        terms of condition priority; if multiple conditions are
        satisfied, the first one will be selected.
    """
    step_id: str
    action: Action
    conditions: dict

    def __str__(self):
        return f"""Step ID: {self.step_id}  Action: {self.action}   Conditions: {[[transitionObject, self.conditions[transitionObject]] for transitionObject in self.conditions]}"""

class Procedure:
    """A sequence of discrete procedure steps."""

    def __init__(self, procedure_id, steps):
        """
        Initialize the procedure.

        Parameters
        ----------

        procedure_id: str
            An identifier for this procedure. Expected to be unique
            within a given procedure suite.

        steps: iterable
            An iterable of ProcedureStep objects ordered from first step
            to last step.
        """
        self.procedure_id = procedure_id
        self.steps = {step.step_id: step for step in steps}

    def __str__(self):
        return f"""Procedure ID: {self.procedure_id}    Steps: {self.steps}"""
