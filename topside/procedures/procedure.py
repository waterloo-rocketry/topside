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

    conditions: list
        A list of tuples (topside.Condition, Transition). Each entry in
        `conditions` represents a conditional transition from this
        ProcedureStep to another step, potentially in a different
        procedure. This list is expected to be ordered in terms of
        condition priority; if multiple conditions are satisfied, the
        first one will be selected.
    """
    step_id: str
    action: Action
    conditions: list


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
        self.steps = {}
        self.step_list = list(steps)
        self.step_id_to_idx = {}

        for i, step in enumerate(steps):
            if step.step_id in self.steps:
                raise ValueError(
                    f'duplicate step ID {step.step_id} encountered in Procedure initialization')
            self.steps[step.step_id] = step
            self.step_id_to_idx[step.step_id] = i

    def index_of(self, step_id):
        """
        Given the ID for a step, return the index at which that step is found.

        Parameters
        ----------

        step_id: str
            The identifier for the step for which the index is desired.

        Returns
        -------

        idx: int
            The positional index of the step with id step_id in this
            procedure.
        """
        return self.step_id_to_idx[step_id]

    def __eq__(self, other):
        return self.procedure_id == other.procedure_id and self.step_list == other.step_list


class ProcedureSuite:
    """A set of procedures and associated metadata."""

    def __init__(self, procedures, starting_procedure_id='main'):
        """
        Initialize the procedure suite.

        Parameters
        ----------

        procedures: iterable
            An iterable of Procedure objects. Each procedure is expected
            to have a unique procedure ID. Order is irrelevant.

        starting_procedure: str
            The procedure ID for the starting procedure used when this
            procedure suite is executed. Defaults to "main" if not
            specified.
        """
        self.starting_procedure_id = starting_procedure_id
        self.procedures = {}

        for proc in procedures:
            if proc.procedure_id in self.procedures:
                raise ValueError(f'duplicate procedure ID {proc.procedure_id} encountered in \
                                   ProcedureSuite initialization')
            self.procedures[proc.procedure_id] = proc

    def __eq__(self, other):
        return self.starting_procedure_id == other.starting_procedure_id and \
            self.procedures == other.procedures

    def __getitem__(self, key):
        return self.procedures[key]
