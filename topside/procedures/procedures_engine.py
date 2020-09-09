from dataclasses import dataclass

import topside as top


class ProceduresEngine:
    """
    An interface for managing Procedure-PlumbingEngine interactions.

    A Procedure is a graph where nodes are ProcedureSteps and edges
    represent transitions between these steps.
    """

    def __init__(self, plumbing_engine=None, suite=None):
        """
        Initialize the ProceduresEngine.

        Parameters
        ----------

        plumbing_engine: topside.PlumbingEngine
            The PlumbingEngine that this ProceduresEngine should manage.

        suite: topside.ProcedureSuite
            The ProcedureSuite that this engine should execute,
            including information about the starting procedure.
        """
        self._plumb = plumbing_engine
        self._suite = None
        self.current_procedure_id = None
        self.current_step = None

        if suite is not None:
            self.load_suite(suite)

    def reset(self):
        """
        Return to the starting procedure and step of the managed suite.

        Does NOT affect the managed plumbing engine.
        """
        # TODO(jacob): When we load a new procedure, we start in the
        # first step, but that means that the action for that step never
        # gets executed (we just start waiting on its conditions
        # immediately). Figure out an elegant way to resolve this.
        if self._suite is not None:
            self.current_procedure_id = self._suite.starting_procedure_id
            self.current_step = self._suite[self.current_procedure_id].step_list[0]

    def load_suite(self, suite):
        """
        Stop managing the current ProcedureSuite and manage a new one.

        Parameters
        ----------

        suite: topside.ProcedureSuite
            The new ProcedureSuite that should be loaded.
        """
        self._suite = suite
        self.reset()

    def execute(self, action):
        """Execute an action on the managed PlumbingEngine if it is not a Miscellaneous Action"""
        if type(action) == top.StateChangeAction:
            self._plumb.set_component_state(action.component, action.state)

    def update_conditions(self):
        """
        Update all current conditions by querying the managed plumbing engine.
        """
        if self._plumb is not None:
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
        if self.current_step is None:
            return False

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
        if self.current_step is not None:
            for condition, transition in self.current_step.conditions:
                if condition.satisfied():
                    new_proc = transition.procedure
                    self.current_procedure_id = new_proc
                    self.current_step = self._suite[new_proc].steps[transition.step]
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
        if self._plumb is not None:
            self._plumb.step(timestep)
            self.update_conditions()

        # TODO(jacob): Consider if this function should return anything
        # about the state of the system: plumbing engine state, current
        # time, etc.

    def current_procedure(self):
        """Return the procedure currently being executed."""
        if self._suite is None:
            return None

        return self._suite[self.current_procedure_id]
