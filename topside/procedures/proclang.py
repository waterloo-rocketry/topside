import copy

from lark import Lark, Transformer

import topside as top


grammar = '''
%import common.LETTER
%import common.DIGIT
%import common.NUMBER
%import common.WS
%ignore WS

document: procedure*
procedure: name ":" step+
name: STRING

step: step_id "." [condition] action deviation*
step_id: STRING

action: "set" component "to" state
component: STRING
state: STRING

deviation: "-" condition transition
transition: name "." step_id

condition: "[" (waituntil | comparison) "]" [":"]

waituntil: time "s"
time: NUMBER

// TODO(jacob): Add support for tolerance in equality comparison.
comparison: node operator value
node: STRING
value: NUMBER
operator: "<"    -> lt
        | ">"    -> gt
        | "<="   -> le
        | ">="   -> ge
        | "=="   -> eq

STRING: (LETTER | DIGIT) (LETTER | DIGIT | "_")*
'''

parser = Lark(grammar, start='document')


class ProcedureTransformer(Transformer):
    """
    Transformer for converting a Lark parse tree to a ProcedureSuite.

    Visits leaf nodes first and only processes a parent node once all of
    its children have been processed. Member functions of this class are
    handlers for the rules of the same names in the grammar described
    above.
    """

    def handle_string(self, orig):
        """
        Utility for processing a generic string in the parse tree.
        """
        (s,) = orig
        return s.value

    def handle_number(self, orig):
        """
        Utility for processing a generic number in the parse tree.
        """
        (n,) = orig
        return float(n)

    def lt(self, data):
        return top.Less

    def gt(self, data):
        return top.Greater

    def le(self, data):
        return top.LessEqual

    def ge(self, data):
        return top.GreaterEqual

    def eq(self, data):
        return top.Equal

    def comparison(self, data):
        comp_class = data[1]
        return comp_class(data[0], data[2])

    def waituntil(self, data):
        return top.WaitUntil(data[0])

    def condition(self, data):
        return data

    def transition(self, data):
        procedure, step = data
        return top.Transition(procedure, step)

    def action(self, data):
        component, state = data
        return top.Action(component, state)

    def step(self, data):
        """
        Process `step` nodes in the parse tree.

        We can't build the steps themselves yet, since the condition for
        advancing to the next step is an annotation on that next step.
        Instead, we build an intermediate step_info dict and then
        process all of the steps in sequence at the next stage.
        """
        step_info = {}
        step_info['id'] = data[0]
        step_info['conditions_out'] = []

        # data will look like one of these, depending on if the step has
        # an attached entry condition:
        #   [id, step entry condition, step action, deviation1, deviation2, ...]
        #   [id, step action, deviation1, deviation2, ...]

        if type(data[1]) == top.Action:  # Step has no attached entry condition
            step_info['condition_in'] = top.Immediate()
            step_info['action'] = data[1]
            deviations = data[2:]
        else:  # Step has an attached entry condition
            step_info['condition_in'] = data[1][0]
            step_info['action'] = data[2]
            deviations = data[3:]

        for cond, transition in deviations:
            step_info['conditions_out'].append((cond[0], transition))

        return step_info

    def procedure(self, data):
        name = data[0]
        steps = []

        # We optionally annotate each step with its entry condition (the
        # optional [p1 < 100] or [500s] before the step), and the
        # preceding step needs that information for its condition set.
        # In order to get that, we iterate over the steps in reverse
        # order and keep track of the most recently processed step, which
        # is the "successor" of the next step we will process.

        successor = None
        for step_info in data[-1:0:-1]:
            conditions = copy.deepcopy(step_info['conditions_out'])
            if successor is not None:
                conditions.append((successor['condition_in'],
                                   top.Transition(name, successor['id'])))
            successor = step_info
            new_step = top.ProcedureStep(step_info['id'], step_info['action'], conditions)
            steps.insert(0, new_step)

        return top.Procedure(name, steps)

    def document(self, data):
        # TODO(jacob): Add support for parsing ProcedureSuite metadata.
        return top.ProcedureSuite(data)

    node = handle_string
    value = handle_number

    time = handle_number

    deviation = tuple

    component = handle_string
    state = handle_string

    name = handle_string
    step_id = handle_string


def parse(text):
    """
    Parse a full ProcLang string and return a procedure suite.

    Parameters
    ----------

    text: str
        A string of ProcLang.

    Returns
    -------

    procedure: list(topside.Procedure)
        A list of all of the procedures described in the ProcLang
        string.
    """

    tree = parser.parse(text)
    return ProcedureTransformer().transform(tree)
