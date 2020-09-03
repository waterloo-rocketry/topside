from dataclasses import dataclass

import topside as top


class ProceduresEngine:
    """
    An interface for managing Procedure-PlumbingEngine interactions.

    A Procedure is a graph where nodes are ProcedureSteps and edges
    represent transitions between these steps.
    """

    def __init__(self, plumbing_engine=None, suite=None, initial_procedure=None, initial_step=None):
        """
        Initialize the ProceduresEngine.

        Parameters
        ----------

        plumbing_engine: topside.PlumbingEngine
            The PlumbingEngine that this ProceduresEngine should manage.

        procedure_suite: iterable
            A procedure suite is any iterable of Procedure objects (but
            typically a list).

        initial_step: str
            The initial procedure step that this ProceduresEngine should
            begin in. Note that the action associated with this step
            will not be executed (unless the step is eventually reached
            again); therefore, this step often has a `None` action and
            a single `Immediate` condition leading directly to the
            actual "first step" of the procedure.
        """
        self._plumb = plumbing_engine
        self._procedure_suite = None
        self.current_procedure_id = initial_procedure
        self.current_step = None

        if suite is not None:
            self._procedure_suite = {proc.procedure_id: proc for proc in suite}

        if suite is not None and initial_procedure is not None and initial_step is not None:
            self.current_step = self._procedure_suite[initial_procedure].steps[initial_step]

    def execute(self, action):
        """Execute an action on the managed PlumbingEngine."""
        self._plumb.set_component_state(action.component, action.state)

    def update_conditions(self):
        """
        Update all current conditions by querying the managed plumbing engine.
        """
        time = self._plumb.time
        pressures = self._plumb.current_pressures()
        state = {'time': time, 'pressures': pressures}

        for condition, _ in self.current_step.conditions:
            condition.update(state)

    def ready_to_advance(self):
        """
        Evaluate if the engine is ready to proceed to a next step.

        Returns True if any condition is satisfied, and False otherwise.
        """
        for condition, _ in self.current_step.conditions:
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
        for condition, transition in self.current_step.conditions:
            if condition.satisfied():
                new_proc = transition.procedure
                self.current_procedure_id = new_proc
                self.current_step = self._procedure_suite[new_proc].steps[transition.step]
                self.execute(self.current_step.action)
                break

    def step_time(self, timestep=None):
        """
        Step the managed plumbing engine in time and update conditions.

        Parameters
        ----------

        timestep: int
            The number of microseconds that the managed plumbing engine
            should be stepped in time by.
        """
        self._plumb.step(timestep)
        self.update_conditions()

        # TODO(jacob): Consider if this function should return anything
        # about the state of the system: plumbing engine state, current
        # time, etc.

    def current_procedure(self):
        """Return the procedure currently being executed."""
        return self._procedure_suite[self.current_procedure_id]
