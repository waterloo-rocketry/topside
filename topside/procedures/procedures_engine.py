from dataclasses import dataclass

import topside as top


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
        A dict mapping topside.Condition objects to step IDs as strings.
        Each entry in `conditions` represents a conditional transition
        from this ProcedureStep to another step with the given ID. This
        dict is expected to be ordered in terms of condition priority;
        if multiple conditions are satisfied, the first one will be
        selected.
    """
    step_id: str
    action: Action
    conditions: dict


class ProceduresEngine:
    """
    An interface for managing Procedure-PlumbingEngine interactions.

    A Procedure is a graph where nodes are ProcedureSteps and edges
    represent transitions between these steps.
    """
    def __init__(self, plumbing_engine=None, procedure=None, initial_step=None):
        """
        Initialize the ProceduresEngine.

        Parameters
        ==========

        plumbing_engine: topside.PlumbingEngine
            The PlumbingEngine that this ProceduresEngine should manage.

        procedure: dict
            A procedure is represented as a dict mapping step_id strings
            to ProcedureSteps.

        initial_step: str
            The initial procedure step that this ProceduresEngine should
            begin in. Note that the action associated with this step
            will not be executed (unless the step is eventually reached
            again); therefore, this step often has a `None` action and
            a single `Immediate` condition leading directly to the
            actual "first step" of the procedure.
        """
        self._plumb = plumbing_engine
        self._procedure = procedure

        if procedure is not None and initial_step is not None:
            self.current_step = self._procedure[initial_step]
        else:
            self.current_step = None

    def execute(self, action):
        """Execute an action on the managed PlumbingEngine."""
        self._plumb.set_component_state(action.component, action.state)

    def ready_to_advance(self):
        """
        Evaluate if the engine is ready to proceed to a next step.

        Returns True if any condition is satisfied, and False otherwise.
        """
        for condition in self.current_step.conditions.keys():
            if condition.satisfied():
                return True
        return False

    def next_step(self):
        """
        Advance to the next step and execute the associated action.

        If multiple conditions are satisfied, this function chooses the
        first one (the highest priority one). If no conditions are
        satisfied, this function does nothing.
        """
        for condition, next_step_id in self.current_step.conditions.items():
            if condition.satisfied():
                self.current_step = self._procedure[next_step_id]
                self.execute(self.current_step.action)
                break
