from abc import ABC, abstractmethod

import topside as top


class Condition(ABC):
    """
    Base class for all procedure conditions.

    This class should never be used directly, so we make it an Abstract
    Base Class (ABC) and mark all of the methods as abstract.
    """

    @abstractmethod
    def reinitialize(self, state):
        """
        Re-initialize any data used by the condition.

        This function is useful for ensuring that "stateful" conditions
        are always reset when their step is first entered. Since steps
        could be encountered multiple times (if the procedure is stepped
        backwards, for example), we need a way of forgetting any data
        that conditions encountered the first time around.
        """
        pass

    @abstractmethod
    def update(self, state):
        """
        Update the condition with the state of the plumbing engine.
        """
        pass

    @abstractmethod
    def satisfied(self):
        """
        Return True if the condition is satisfied and False otherwise.
        """
        pass


class Immediate:
    """Condition that is always satisfied."""

    def __str__(self):
        return 'Immediately'

    def reinitialize(self, state):
        """Re-initialize the condition; a no-op."""
        pass

    def update(self, state):
        """Update the condition with the latest state; a no-op."""
        pass

    def satisfied(self):
        """Return True, since this condition is always satisfied."""
        return True

    def __eq__(self, other):
        return type(other) == Immediate


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

    def __str__(self):
        return '(' + ' and '.join([str(cond) for cond in self._conditions]) + ')'

    def reinitialize(self, state):
        """
        Re-initialize all child conditions.

        Parameters
        ----------

        state: dict
            state is expected to contain all information necessary for
            each condition to properly re-initialize. In most cases,
            this will mean either a `time` item or a `pressures` item.
        """
        for cond in self._conditions:
            cond.reinitialize(state)

    def update(self, state):
        """
        Update all conditions with the latest state.

        Parameters
        ----------

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

    def __eq__(self, other):
        return type(self) == type(other) and self._conditions == other._conditions

    def export(self, fmt):
        if fmt == top.ExportFormat.Latex:
            return ' and '.join([cond.export(fmt) for cond in self._conditions])
        else:
            raise NotImplementedError(f'Format "{fmt}" not supported')


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

    def __str__(self):
        return '(' + ' or '.join([str(cond) for cond in self._conditions]) + ')'

    def reinitialize(self, state):
        """
        Initialize all child conditions.

        Parameters
        ----------

        state: dict
            state is expected to contain all information necessary for
            each condition to properly re-initialize. In most cases,
            this will mean either a `time` item or a `pressures` item.
        """
        for cond in self._conditions:
            cond.reinitialize(state)

    def update(self, state):
        """
        Update all conditions with the latest state.

        Parameters
        ----------

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

    def __eq__(self, other):
        return type(self) == type(other) and self._conditions == other._conditions

    def export(self, fmt):
        if fmt == top.ExportFormat.Latex:
            return ' or '.join([cond.export(fmt) for cond in self._conditions])
        else:
            raise NotImplementedError(f'Format "{fmt}" not supported')


class WaitFor:
    """Condition that is satisfied once an amount of time has elapsed."""

    def __init__(self, wait_t):
        """
        Initialize the condition.

        Parameters
        ----------

        wait_t: int
            The wait time interval for this condition, in microseconds.
            This condition will become satisfied `wait_t` after it first
            becomes active (its step is reached).
        """
        self.wait_t = wait_t
        self.current_t = None
        self.target_t = None

    def __str__(self):
        return f'Wait for {round(self.wait_t / 1e6)} seconds'

    def reinitialize(self, state):
        """
        Re-initialize the condition.

        Resets the current time and sets the target time based on the
        configured wait time.

        Parameters
        ----------

        state: dict
            state is expected to have the key 'time', with the value of
            state['time'] representing the current time for the plumbing
            engine.
        """
        self.current_t = state['time']
        self.target_t = self.current_t + self.wait_t

    def update(self, state):
        """
        Update the current time with the latest state.

        Parameters
        ----------

        state: dict
            state is expected to have the key 'time', with the value of
            state['time'] representing the current time for the plumbing
            engine.
        """
        self.current_t = state['time']

    def satisfied(self):
        """Return True if wait_t has elapsed and False otherwise."""
        if self.target_t is None or self.current_t is None:
            return False
        return self.current_t >= self.target_t

    def __eq__(self, other):
        return type(self) == type(other) and self.wait_t == other.wait_t

    def export(self, fmt):
        if fmt == top.ExportFormat.Latex:
            return f'{round(self.wait_t / 1e6)} seconds'
        else:
            raise NotImplementedError(f'Format "{fmt}" not supported')


class Comparison:
    """Base class for conditions comparing a pressure to a reference."""

    def __init__(self, node, pressure):
        """
        Initialize the Comparison condition.

        The Comparison base class should not be instantiated directly;
        instead, use one of the derived classes, like LessEqual or
        Greater.

        Parameters
        ----------

        node: str
            The node that this condition is responsible for monitoring.

        pressure: float
            The reference pressure that will be used in evaluating
            comparisons.
        """
        self.node = node
        self.reference_pressure = pressure
        self.current_pressure = None

    def reinitialize(self, state):
        """
        Re-initialize the condition.

        Since Comparison conditions only need to keep track of one piece
        of data, re-initialization is the same as updating.

        Parameters
        ----------

        state: dict
            state is expected to be a dict of the form:
              {'pressures': {self.node: P}}
            where P is the current pressure at node self.node.
        """
        self.update(state)

    def compare(self, current_pressure, reference_pressure):
        """
        Evaluates the comparison and returns the result.

        This method must be overridden in classes inheriting from
        Comparison.
        """
        raise NotImplementedError('Comparison base class cannot be used directly')

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

    def __eq__(self, other):
        return type(self) == type(other) and \
            self.node == other.node and \
            self.reference_pressure == other.reference_pressure


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

    def __str__(self):
        return f'{self.node} == {round(self.reference_pressure)}'

    def compare(self, current_pressure, reference_pressure):
        """Return True if the pressures differ by less than eps."""
        return abs(current_pressure - reference_pressure) <= self.eps

    def __eq__(self, other):
        return type(self) == type(other) and \
            self.node == other.node and \
            self.reference_pressure == other.reference_pressure and \
            self.eps == other.eps

    def export(self, fmt):
        if fmt == top.ExportFormat.Latex:
            return f'{self.node} is equal to {round(self.reference_pressure)}psi'
        else:
            raise NotImplementedError(f'Format "{fmt}" not supported')


class Less(Comparison):
    """Condition that tests if a pressure is less than a reference."""

    def __str__(self):
        return f'{self.node} < {round(self.reference_pressure)}'

    def compare(self, current_pressure, reference_pressure):
        """Compare pressures using less-than."""
        return current_pressure < reference_pressure

    def export(self, fmt):
        if fmt == top.ExportFormat.Latex:
            return f'{self.node} is less than {round(self.reference_pressure)}psi'
        else:
            raise NotImplementedError(f'Format "{fmt}" not supported')


class Greater(Comparison):
    """Condition that tests if a pressure is greater than a reference."""

    def __str__(self):
        return f'{self.node} > {round(self.reference_pressure)}'

    def compare(self, current_pressure, reference_pressure):
        """Compare pressures using greater-than."""
        return current_pressure > reference_pressure

    def export(self, fmt):
        if fmt == top.ExportFormat.Latex:
            return f'{self.node} is greater than {round(self.reference_pressure)}psi'
        else:
            raise NotImplementedError(f'Format "{fmt}" not supported')


class LessEqual(Comparison):
    """Condition that tests if a pressure is less than or equal to a reference."""

    def __str__(self):
        return f'{self.node} <= {round(self.reference_pressure)}'

    def compare(self, current_pressure, reference_pressure):
        """Compare pressures using less-than-or-equal."""
        return current_pressure <= reference_pressure

    def export(self, fmt):
        if fmt == top.ExportFormat.Latex:
            return f'{self.node} is less than or equal to {round(self.reference_pressure)}psi'
        else:
            raise NotImplementedError(f'Format "{fmt}" not supported')


class GreaterEqual(Comparison):
    """Condition that tests if a pressure is greater than or equal to a reference."""

    def __str__(self):
        return f'{self.node} >= {round(self.reference_pressure)}'

    def compare(self, current_pressure, reference_pressure):
        """Compare pressures using greater-than-or-equal."""
        return current_pressure >= reference_pressure

    def export(self, fmt):
        if fmt == top.ExportFormat.Latex:
            return f'{self.node} is greater than or equal to {round(self.reference_pressure)}psi'
        else:
            raise NotImplementedError(f'Format "{fmt}" not supported')
