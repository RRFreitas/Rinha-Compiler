import json
import enum

class Kind(enum.Enum):
    IF = "If"
    LET = "Let"
    STR = "Str"
    BOOL = "Bool"
    INT = "Int"
    BINARY_OP = "BinaryOp"
    BINARY = "Binary"
    CALL = "Call"
    FUNCTION = "Function"
    PRINT = "Print"
    VAR = "Var"

variables = {}

class Term():
    
    def __init__(self, kind: Kind) -> None:
        self.kind = kind

    def evaluate(self) -> any:
        pass

class Parameter(Term):

    def __init__(self, kind: Kind, text: str) -> None:
        super().__init__(kind)
        self.text = text

class Let(Term):

    def __init__(self, kind: Kind, name: Parameter, value: Term, next: Term) -> None:
        super().__init__(kind)
        self.name = name
        self.value = value
        self.next = next

    def evaluate(self):
        variables[self.name.text] = self.value.evaluate()
        if self.next != None:
            return self.next.evaluate()

class Var(Term):

    def __init__(self, kind: Kind, text: str) -> None:
        super().__init__(kind)
        self.text = text

    def evaluate(self) -> any:
        return variables[self.text]

class Int(Term):

    def __init__(self, kind: Kind, value: int) -> None:
        super().__init__(kind)
        self.value = value
    
    def evaluate(self):
        return self.value

class Bool(Term):

    def __init__(self, kind: Kind, value: bool) -> None:
        super().__init__(kind)
        self.value = value

    def evaluate(self) -> any:
        return self.value

class Str(Term):
    
    def __init__(self, kind: Kind, value: str) -> None:
        super().__init__(kind)
        self.value = value

    def evaluate(self) -> any:
        return self.value

class BinaryOp(Term):

    def __init__(self, kind: Kind, name: str) -> None:
        super().__init__(kind)
        self.name = name

    def evaluate(self, a: any, b: any) -> any:
        match self.name:
            case "Add":
                return a + b
            case "Sub":
                return a - b
            case "Mul":
                return a * b
            case "Div":
                return a / b
            case "Eq":
                return a == b
            case "Lt":
                return a < b
            case "Gt":
                return a > b
            case "Eq":
                return a == b
            case "Neg":
                return a != b
            case "Lte":
                return a <= b
            case "Gte":
                return a <= b
            case "And":
                return a and b
            case "Or":
                return a or b

class Binary(Term):

    def __init__(self, kind: Kind, lhs: Term, op: BinaryOp, rhs: Term) -> None:
        super().__init__(kind)
        self.lhs = lhs
        self.op = op
        self.rhs = rhs

    def evaluate(self) -> any:
        return self.op.evaluate(self.lhs.evaluate(), self.rhs.evaluate())

class Print(Term):
    
    def __init__(self, kind: Kind, value: Term) -> None:
        super().__init__(kind)
        self.value = value

    def evaluate(self) -> any:
        print(self.value.evaluate())

class If(Term):

    def __init__(self, kind: Kind, condition: Term, then: Term, otherwise: Term) -> None:
        super().__init__(kind)
        self.condition = condition
        self.then = then
        self.otherwise = otherwise

    def evaluate(self) -> any:
        if self.condition.evaluate():
            return self.then.evaluate()
        elif self.otherwise != None:
            return self.otherwise.evaluate()
        else:
            return None

class Function(Term):

    def __init__(self, kind: Kind, parameters: list[Parameter], value: Term) -> None:
        super().__init__(kind)
        self.parameters = parameters
        self.value = value

    def evaluate(self) -> any:
        return self
    
    def call(self) -> any:
        return self.value.evaluate()
class Call(Term):

    def __init__(self, kind: Kind, callee: Var, arguments: list[Term]) -> None:
        super().__init__(kind)
        self.callee = callee
        self.arguments = arguments

    def evaluate(self) -> any:
        #assert len(self.arguments) == len(self.callee.parameters)
        global variables
        func = variables[self.callee.text]
        old_variables = variables.copy()
        for argument, param in zip(self.arguments, func.parameters):
            variables[param.text] = argument.evaluate()
        value = func.call()
        variables = old_variables
        return value

class Interpreter():
    
    def __init__(self, name: str, expression: Term) -> None:
        self.name = name
        self.expression = expression

    def evaluate(self):
        self.expression.evaluate()

def parse(tree):
    print(tree["kind"])
    match tree["kind"]:
        case Kind.LET.value:
            has_next = tree.get("next", False)
            return Let(
                kind      = tree["kind"],
                name      = Parameter(kind="Parameter", text=tree["name"]["text"]),
                value     = parse(tree["value"]), 
                next      = None if not has_next else parse(tree["next"])
            )
        case Kind.PRINT.value:
            return Print(
                kind = tree["kind"],
                value = parse(tree["value"])
            )
        case Kind.BINARY.value:
            return Binary(
                kind = tree["kind"],
                lhs  = parse(tree["lhs"]),
                op   = BinaryOp(kind = "BinaryOp", name = tree["op"]),
                rhs  = parse(tree["rhs"])
            )
        case Kind.INT.value:
            return Int(
                kind = tree["kind"],
                value = tree["value"]
            )
        case Kind.VAR.value:
            return Var(
                kind = tree["kind"],
                text = tree["text"]
            )
        case Kind.BOOL.value:
            return Bool(
                kind = tree["kind"],
                value = bool(tree["value"])
            )
        case Kind.IF.value:
            return If(
                kind      = tree["kind"],
                condition = parse(tree["condition"]),
                then      = parse(tree["then"]),
                otherwise = parse(tree["otherwise"])
            )
        case Kind.FUNCTION.value:
            return Function(
                kind       = tree["kind"],
                parameters = [Parameter("parameter", param["text"]) for param in tree["parameters"]],
                value      = parse(tree["value"]) 
            )
        case Kind.CALL.value:
            return Call(
                kind      = tree["kind"],
                callee    = parse(tree["callee"]),
                arguments = [parse(arg) for arg in tree["arguments"]]
            )
        case Kind.STR.value:
            return Str(
                kind = tree["kind"],
                value = tree["value"]
            )

def parse_ast(tree: dict) -> Interpreter:
    return Interpreter(tree["name"], parse(tree["expression"]))

with open("/var/rinha/source.rinha.json") as f:
    tree = json.loads(f.read())

    interpreter = parse_ast(tree)
    interpreter.evaluate()
