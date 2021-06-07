from enum import Enum
import copy
import queue

import topside as top


class StepPosition(Enum):
    Before = 1
    After = 2


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
        self.step_position = None
        self.state_stack = None #queue.LifoQueue() ##I know, I also can't believe that they're called lifoQueue's and not stacks

        if suite is not None:
            self.load_suite(suite)

    def reset(self):
        """
        Return to the starting procedure and step of the managed suite.

        Does NOT affect the managed plumbing engine.
        """
        if self._suite is not None:
            self.current_procedure_id = self._suite.starting_procedure_id
            self.current_step = self._suite[self.current_procedure_id].step_list[0]
            self.step_position = StepPosition.Before

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
        if isinstance(action, top.StateChangeAction):
            if self._plumb is not None:
                self._plumb.set_component_state(action.component, action.state)

    def reinitialize_conditions(self):
        """
        Re-initialize all current conditions by querying the managed plumbing engine.
        """
        if self._plumb is not None and self.current_step is not None:
            time = self._plumb.time
            pressures = self._plumb.current_pressures()
            state = {'time': time, 'pressures': pressures}

            for condition, _ in self.current_step.conditions:
                condition.reinitialize(state)

    def update_conditions(self):
        """
        Update all current conditions by querying the managed plumbing engine.
        """
        if self._plumb is not None and self.current_step is not None:
            time = self._plumb.time
            pressures = self._plumb.current_pressures()
            state = {'time': time, 'pressures': pressures}

            for condition, _ in self.current_step.conditions:
                condition.update(state)

    def execute_current(self):
        """
        Execute the action associated with the current step.

        This function only has an effect if called from a pre-node. When
        called, it moves the engine to the current step's post-node.
        """
        if self.current_step is None or self.step_position == StepPosition.After:
            return

        self.push_stack()
        self.execute(self.current_step.action)
        self.step_position = StepPosition.After
        self.reinitialize_conditions()

    def ready_to_proceed(self):
        """
        Evaluate if the engine is ready to proceed to a next step.

        Returns False if the engine is in a pre-node, since 'proceed' is
        only valid from a post-node. If in a post-node, returns True if
        any condition is satisfied and False otherwise.
        """
        if self.current_step is None or self.step_position == StepPosition.Before:
            return False

        for condition, _ in self.current_step.conditions:
            if condition.satisfied():
                return True
        return False

    def proceed(self):
        """
        Move from the current step post-node to the next step pre-node.

        If multiple conditions are satisfied, this function chooses the
        first one (the highest priority one). If no conditions are
        satisfied, this function does nothing.
        """
        if self.current_step is None or self.step_position == StepPosition.Before:
            return

        for condition, transition in self.current_step.conditions:
            if condition.satisfied():
                self.push_stack()
                new_proc = transition.procedure
                self.current_procedure_id = new_proc
                self.current_step = self._suite[new_proc].steps[transition.step]
                self.step_position = StepPosition.Before
                break

    def next_step(self):
        """
        Execute the next step in the queue.

        This function can be called whether the engine is in a post-node
        or a pre-node. After calling this function, the engine will end
        in the post-node of the next step to be executed.
        """
        self.proceed()
        self.execute_current()

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

    def push_stack(self):
        curent_plumb = copy.deepcopy(self._plumb)
        prod_id = self.current_procedure_id
        step = copy.deepcopy(self.current_step)
        step_pos = self.step_position

        #self.state_stack.put((curent_plumb, prod_id, step, step_pos))
        self.state_stack = ((curent_plumb, prod_id, step, step_pos), self.state_stack)

    def pop_and_set_stack(self):
        if(not self.state_stack == None): ##not self.state_stack.empty()
            stack_element = self.state_stack[0]
            
            self._plumb = stack_element[0]
            self.current_procedure_id = stack_element[1]
            self.current_step = stack_element[2]
            self.step_position = stack_element[3]

            self.state_stack = self.state_stack[1]

            return stack_element[0]##debug