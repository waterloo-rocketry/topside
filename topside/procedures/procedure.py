from dataclasses import dataclass
import enum
import typing

import topside as top


class ExportFormat(enum.Enum):
    Latex = 1


# TODO(jacob): Investigate whether this would be better as a variant
# rather than a base class.
class Action:
    pass


@dataclass
class StateChangeAction(Action):
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

    def export(self, fmt):
        if fmt == top.ExportFormat.Latex:
            if self.state == 'open':
                return 'Open ' + self.component
            elif self.state == 'closed':
                return 'Close ' + self.component
            else:
                return 'Set ' + self.component + ' to ' + self.state
        else:
            raise NotImplementedError(f'Format "{fmt}" not supported')


@dataclass
class MiscAction(Action):
    """
    A procedure action that does not fit into any other category.

    Members
    -------
    action_type: str
        The string specifies which type of action it is.
    """
    action_type: str

    def export(self, fmt):
        if fmt == top.ExportFormat.Latex:
            return self.action_type
        else:
            raise NotImplementedError(f'Format "{fmt}" not supported')


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

    operator: str
        The person who performs the step
    """
    step_id: str
    action: Action
    conditions: list
    operator: str

    def export(self, fmt):
        if fmt == top.ExportFormat.Latex:
            retval = ''
            if self.operator != '':
                retval += '\\' + self.operator + '{} '
            retval += self.action.export(fmt)
            return retval
        else:
            raise NotImplementedError(f'Format "{fmt}" not supported')


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
        return type(self) == type(other) and \
            self.procedure_id == other.procedure_id and \
            self.step_list == other.step_list

    def export(self, fmt):
        if fmt == top.ExportFormat.Latex:
            export_val = f'\\subsection{{{self.procedure_id}}}'
            if len(self.step_list) > 0:
                export_val += '\n\\begin{checklist}'
                for index, step in enumerate(self.step_list):
                    export_val += '\n    \\item ' + step.export(fmt)
                    wait_condition = ''
                    jump_conditions = ''
                    for t in step.conditions:
                        if not isinstance(t[0], top.Immediate) and \
                           t[1].procedure == self.procedure_id and \
                           t[1].step == self.step_list[index + 1].step_id:
                            wait_condition = '\n    \\item Wait ' + t[0].export(fmt)
                        elif not isinstance(t[0], top.Immediate):
                            cond = '\n    \\item If ' + t[0].export(fmt)
                            beg = '\n    \\begin{checklist}'
                            action = '\n        \\item Begin ' + t[1].procedure + ' procedure'
                            end = '\n    \\end{checklist}'
                            jump_conditions += cond + beg + action + end
                    export_val += jump_conditions
                    export_val += wait_condition
                export_val += '\n\\end{checklist}'
            return export_val
        else:
            raise NotImplementedError(f'Format "{fmt}" not supported')


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

        # TODO(jacob): Allow invalid procedure suites to be created, but
        # keep track of the invalid reasons (same way plumbing code
        # works).

        for proc in procedures:
            if proc.procedure_id in self.procedures:
                raise ValueError(f'duplicate procedure ID {proc.procedure_id} encountered in '
                                 + 'ProcedureSuite initialization')
            self.procedures[proc.procedure_id] = proc

        if self.starting_procedure_id not in self.procedures:
            raise ValueError(f'starting procedure ID {self.starting_procedure_id} not found in '
                             + 'procedure dict')

    def __eq__(self, other):
        return type(self) == type(other) and \
            self.starting_procedure_id == other.starting_procedure_id and \
            self.procedures == other.procedures

    def __getitem__(self, key):
        return self.procedures[key]

    def export(self, fmt):
        if fmt == top.ExportFormat.Latex:
            exported_procedures = []
            exported_procedures.append(self.procedures[self.starting_procedure_id].export(fmt))
            for proc in self.procedures:
                if proc == self.starting_procedure_id:
                    continue
                exported_procedures.append(self.procedures[proc].export(fmt))
            # TODO(aaron): properly sanitize latex characters, not just escaping _'s
            return '\n\n'.join(exported_procedures).replace('_', '\\_')
        else:
            raise NotImplementedError(f'Format "{fmt}" not supported')
