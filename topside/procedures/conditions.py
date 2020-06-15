class Immediate:
    """Condition that is always satisfied."""

    def update(self, state):
        """Update the condition with the latest state; a no-op."""
        pass

    def satisfied(self):
        """Return True, since this condition is always satisfied."""
        return True


class And:
    """
    Condition representing a logical AND of multiple other conditions.
    """

    def __init__(self, conditions):
        """
        Initialize the condition.

        Parameters
        ----------

        conditions: list
            A list of conditions that must all be satisfied for this
            condition to be satisfied.
        """
        self._conditions = conditions

    def update(self, state):
        """
        Update all conditions with the latest state.

        Parameters
        ==========

        state: dict
            state is expected to contain all information necessary for
            each condition to properly update. In most cases, this will
            mean either a `time` item or a `pressures` item.
        """
        for cond in self._conditions:
            cond.update(state)

    def satisfied(self):
        """
        Return True if all conditions are satisfied and False otherwise.
        """
        for cond in self._conditions:
            if not cond.satisfied():
                return False
        return True


class Or:
    """
    Condition representing a logical OR of multiple other conditions.
    """

    def __init__(self, conditions):
        """
        Initialize the condition.

        Parameters
        ----------

        conditions: list
            A list of conditions that must all be satisfied for this
            condition to be satisfied.
        """
        self._conditions = conditions

    def update(self, state):
        """
        Update all conditions with the latest state.

        Parameters
        ==========

        state: dict
            state is expected to contain all information necessary for
            each condition to properly update. In most cases, this will
            mean either a `time` item or a `pressures` item.
        """
        for cond in self._conditions:
            cond.update(state)

    def satisfied(self):
        """
        Return True if any condition is satisfied and False otherwise.
        """
        for cond in self._conditions:
            if cond.satisfied():
                return True
        return False


class WaitUntil:
    """Condition that is satisfied once a certain time is reached."""

    def __init__(self, t):
        """
        Initialize the condition.

        Parameters
        ----------

        t: int
            The reference time for this condition. Once t is reached,
            this condition will be satisfied. t should be in the same
            units and use the same timebase as the PlumbingEngine
            (integer microseconds from simulation start).
        """
        self.target_t = t
        self.current_t = None

    def update(self, state):
        """
        Update the condition with the latest state.

        Parameters
        ----------

        state: dict
            state is expected to have the key 'time', with the value of
            state['time'] representing the current time for the plumbing
            engine.
        """
        self.current_t = state['time']

    def satisfied(self):
        """Return True if satisfied and False otherwise."""
        if self.current_t is None:
            return False
        return self.current_t >= self.target_t


class Comparison:
    """Base class for conditions comparing a pressure to a reference."""

    def __init__(self, node, pressure, comp_fn=None):
        """
        Initialize the Comparison condition.

        If using the Comparison base class directly, the comp_fn
        parameter is required.

        Parameters
        ----------

        node: str
            The node that this condition is responsible for monitoring.

        pressure: float
            The reference pressure that will be used in evaluating
            comparisons.

        comp_fn: function object
            comp_fn is expected to have the following signature:
              comp_fn(curr_pressure: float, ref_pressure: float) -> bool
            This function compares the current pressure to the set
            reference and returns True if the comparison passes.
        """
        self.node = node
        self.reference_pressure = pressure
        self.current_pressure = None
        self.comp_fn = comp_fn

    def compare(self, current_pressure, reference_pressure):
        """
        Evaluates the custom comp_fn and returns the result.

        This method should be overridden in classes inheriting from
        Comparison.
        """
        if self.comp_fn is None:
            raise NotImplementedError('Comparison base class requires a custom comparison function')
        return self.comp_fn(self.current_pressure, self.reference_pressure)

    def update(self, state):
        """
        Update the condition with the latest state.

        Parameters
        ----------

        state: dict
            state is expected to be a dict of the form:
              {'pressures': {self.node: P}}
            where P is the current pressure at node self.node.
        """
        self.current_pressure = state['pressures'][self.node]

    def satisfied(self):
        """Return True if satisfied and False otherwise."""
        if self.current_pressure is None:
            return False
        return self.compare(self.current_pressure, self.reference_pressure)


class Equal(Comparison):
    """
    Condition that is satisfied if a pressure is equal to a reference.

    Optionally, a tolerance may be specified; if so, the condition is
    satisfied if the pressure is within some margin of the reference.
    """

    def __init__(self, node, pressure, eps=0):
        """
        Initialize the condition.

        Parameters
        ----------

        node: str
            The node that this condition is responsible for monitoring.

        pressure: float
            The reference pressure that will be used in evaluating
            comparisons.

        eps: float
            The absolute margin by which the node pressure is permitted
            to deviate from the reference for the condition to be
            satisfied. Defaults to 0.
        """
        self.eps = eps
        Comparison.__init__(self, node, pressure)

    def compare(self, current_pressure, reference_pressure):
        """Return True if the pressures differ by less than eps."""
        return abs(current_pressure - reference_pressure) <= self.eps


class Less(Comparison):
    """Condition that tests if a pressure is less than a reference."""

    def compare(self, current_pressure, reference_pressure):
        """Compare pressures using less-than."""
        return current_pressure < reference_pressure


class Greater(Comparison):
    """Condition that tests if a pressure is greater than a reference."""

    def compare(self, current_pressure, reference_pressure):
        """Compare pressures using greater-than."""
        return current_pressure > reference_pressure


class LessEqual(Comparison):
    """Condition that tests if a pressure is less than or equal to a reference."""

    def compare(self, current_pressure, reference_pressure):
        """Compare pressures using less-than-or-equal."""
        return current_pressure <= reference_pressure


class GreaterEqual(Comparison):
    """Condition that tests if a pressure is greater than or equal to a reference."""

    def compare(self, current_pressure, reference_pressure):
        """Compare pressures using greater-than-or-equal."""
        return current_pressure >= reference_pressure
