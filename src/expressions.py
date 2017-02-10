"""
expressions.py
----------------------------------------

Implementation of objects to represent parsed
Scheme code. All Scheme code consists of expressions,
which can either be atoms, or lists or expressions.
Lists are represented in using Pair objects following
the usually Scheme convention.

This module also provides utility functions to aid the compiler
in evaluating each expression.

"""


class Pair:
    """
    Represents a Scheme pair. `first` and `second`
    are public attributes.

    Common Scheme list operations can be done on Pair object. eg:

    car -> Pair.first
    cdr -> Pair.second
    cadr -> Pair.second.first
    caadr -> Pair.second.first.first
    ...
    """
    def __init__(self, first, second):
        # Sometimes, a Pair will be empty,
        # and None values will be passed
        # in. Replace them with empty strings
        # instead.
        self.first = first
        self.second = second

    def __repr__(self):
        obj = self
        repr_ = '(' + repr(obj.first)
        while isinstance(obj.second, Pair):
            repr_ += ' ' + repr(obj.second.first)
            obj = obj.second
        if isinstance(obj.second, Nil):
            repr_ += ')'
        else:
            repr_ += ' . ' + repr(obj.second) + ')'
        return repr_
            
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.first == other.first and self.second == other.second
        return False


class Number:
    """
    Number objects represent integer types in Scheme.
    """
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return str(self.value)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.value == other.value
        return self.value == other


class Symbol:
    """
    Symbol objects represent symbols(a.k.a variables) in Scheme.
    """
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return self.value

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.value == other.value
        else:
            return self.value == other

    
class Boolean:
    """
    Boolean objects represent the booleans values in Scheme.
    """
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return '#t' if self.value else '#f'

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.value == other.value
        return False


class Nil:
    """
    Represents "nil" values in Scheme.
    """
    def __init__(self):
        self.value = '()'

    def __repr__(self):
        return self.value

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.value == other.value
        return False


class ExpressionError(Exception):
    """
    An error to raise if an expression is
    not syntactically valid.
    """


def expand_nested_pairs(pair, recursive=False):
    """
    Expand nested pair objects, into a flat Python list.
    if recursive is True, nested, nested pair objects are
    expanded as well. eg.

    recursive is True:
        [[1, 2, 3, [4, 5, 6]]] -> [1, 2, 3, 4, 5, 6]
    recursive is False:
        [[1, 2, 3, [4, 5, 6]]] -> [1, 2, 3, [4, 5, 6]]
    """
    lst = []
    while isinstance(pair, Pair):
        head = pair.first
        if recursive and isinstance(head, Pair):
            lst.append(expand_nested_pairs(head))
        else:
            lst.append(head)
        pair = pair.second
    return lst


def make_nested_pairs_from_seq(*args):
    """
    Given a list of arguments, creates a list in Scheme representation
    (nested Pairs).
    """
    if not args:
        return Nil()
    return Pair(args[0], make_nested_pairs_from_seq(*args[1:]))


def is_scheme_expression(expr):
    """
    Is the given expression a valid Scheme expression.
    """
    return expr is None or is_const(expr) or is_variable(expr) or isinstance(expr, Pair)


def is_tagged(expr, tag):
    """
    Check if the given expression's .first attribute is
    equal to the given tag.
    """
    return expr.first == tag


def is_null(expr):
    """
    Check if the expression in "null".
    """
    return isinstance(expr, Nil)


def is_const(expr):
    """
    Check if the expression is a constant value.
    """
    return isinstance(expr, (Number, Boolean))


def is_variable(expr):
    """
    Check if the expression is a variable.
    """
    return isinstance(expr, Symbol)


def is_quoted(expr):
    """
    Check if the expressions is quoted.
    """
    return is_tagged(expr, "quote")


def is_assignment(expr):
    """
    Check if the expression is an assignment.
    """
    return is_tagged(expr, 'set!')


def is_begin(expr):
    """
    Check if the expression is a list of
    expressions(is a "begin" expression).
    """
    return is_tagged(expr, 'begin')


def is_definition(expr):
    """
    Check if the expression is a
    definition.
    """
    return is_tagged(expr, 'define')


def is_if(expr):
    """
    Check if the given expression is
    an if expression.
    """
    return is_tagged(expr, 'if')


def is_cond(expr):
    return is_tagged(expr, 'cond')


def is_lambda(expr):
    """
    Check if the given expression is a lambda.
    """
    return is_tagged(expr, 'lambda')


def is_proc_call(expr):
    """
    Check if the given expression is a procedure call. eg.
    "(+ 1 2)", where "+" is the procedure.
    """
    return isinstance(expr, Pair)


# Helper functions to make accessing specific values in Pair
# objects easier.

def variable_name(expr):
    return expr.second.first


def variable_value(expr):
    return expr.second.second.first


def if_cond(expr):
    return expr.second.first


def if_then(expr):
    return expr.second.second.first


def if_else(expr):
    return expr.second.second.second.first


def definition_value(expr):
    if isinstance(expr.second.first, Symbol):
        return expr.second.second.first
    else:
        # support the formal definition of lambda's
        # by extending a lambda from the formal
        # expression.
        return make_lambda(expr.second.first.second,
                           expr.second.second)


def definition_variable(expr):
    if isinstance(expr.second.first, Symbol):
        return expr.second.first
    else:
        return expr.second.first.first


def lambda_parameters(expr):
    return expr.second.first


def lambda_body(expr):
    return expr.second.second


def lambda_name(expr):
    return expr.first


def make_lambda(parameters, body):
    return Pair(Symbol('lambda'), Pair(parameters, body))


def cond_actions(clause):
    return clause.second


def cond_clauses(expr):
    return expr.second


def make_ifs_from_cond(clauses):
    """
    Given a cond expression, convert to a chain of if
    expressions.
    """
    # if there are not clauses, return #f
    if isinstance(clauses, Nil):
        return Boolean(False)

    first = clauses.first
    rest = clauses.second

    if is_tagged(first, Symbol('else')):
        if isinstance(rest, Nil):
            return sequence_to_expression(cond_actions(first))
        else:
            raise ExpressionError('"else" is not the last expression '
                                  'in cond: {}'.format(repr(clauses)))
    else:
        return make_if(
            cond=first.first,
            then=sequence_to_expression(cond_actions(first)),
            _else=make_ifs_from_cond(rest)
        )


def make_if(cond, then, _else):
    return make_nested_pairs_from_seq(Symbol('if'), cond, then, _else)


def sequence_to_expression(exprs):
    """
    Convert a list of expressions to a single expression.
    Add a begin expression if it is more than one expression.
    """
    if isinstance(exprs, Nil):
        return Nil()
    elif isinstance(exprs.second, Nil):
        return exprs.first
    else:
        return Pair(Symbol('begin'), exprs)


def quoted_text(expr):
    return expr.second.first


def begin_body(expr):
    return expr.second


def procedure_args(expr):
    return expr.second


def procedure_op(expr):
    return expr.first
