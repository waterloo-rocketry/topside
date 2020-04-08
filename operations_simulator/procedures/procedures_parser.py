from lark import Lark, Transformer

grammar = """
    start: expr+

    ?expr: action
        | "if"i cond expr+ "else"i expr+ "end"i -> twobranch
        | "if"i cond expr+ "end"i               -> onebranch
        | "when"i cond expr                     -> when

    ?action: VERB VALVE
          | "abort"i                           -> abort
          | "read"i PRESSURE                   -> read

    cond: PRESSURE CMP NUMBER
        | NUMBER CMP PRESSURE
        | NUMBER CMP NUMBER
        | PRESSURE CMP PRESSURE

    CMP: ">=" | "<=" | "=" | ">" | "<"
    VERB: "open"i | "close"i

    VALVE: (LETTER | "_")+
    PRESSURE: (LETTER | "_")+

    %import common.LETTER
    %import common.WS
    %import common.INT -> NUMBER
    %ignore WS"""

def _indent(text, count):
    padding = count * ' '
    return ''.join(padding+line for line in text.splitlines(True))

class print_ops(Transformer):
    def action(self, action):
        if action[0].type == "VERB" and action[1].type == "VALVE":
            return f"{action[0].value} {action[1].value}"
        return ""
    def abort(self, abort):
        return "ABORT"

    def cond(self, cond):
        if cond[0].type == "PRESSURE" and cond[1].type == "CMP" and cond[2].type == "NUMBER":
            return f"{cond[0].value} {cond[1].value} {cond[2].value}"
        return ""

    def onebranch(self, thing):
        cond = thing[0]
        expr = thing[1]
        if type(expr) == str:
            return f"if {cond}\n" + _indent(expr, 4) + "\nend"
        return ""

    def twobranch(self, thing):
        cond = thing[0]
        expr_true = thing[1]
        expr_false = thing[2]
        return f"if {cond}\n{_indent(expr_true,4)}\nelse\n{_indent(expr_false,4)}\nend"

    def start(self, thing):
        return '\n'.join(thing)

class Parser:
    def __init__(self):
        self.parser = Lark(grammar)
        self.ast = None
        pass

    def read_ops(self, text):
        parsed = self.parser.parse(text)
        if self.ast == None:
            self.ast = parsed
        else:
            self.ast.children += parsed.children
            pass

    def pretty_print(self):
        """pretty print the ast as we currently have it"""
        print(print_ops().transform(self.ast))

p = Parser()
p.read_ops("open remote_fill close remote_vent if tank_pressure > 100 if tank_pressure < 200 open remote_fill end else abort end")
p.pretty_print()
