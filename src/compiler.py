"""
compiler.py
----------------------------------------

This module contains the implementation of the
Scheme compiler for Schemey. It takes in one
or more expressions(a list of Pair objects), and generates
a code object ready for serialization and/or direct
execution by the virtual machine.

"""

from bytecode import *
from expressions import *
from utils import flatten, find_or_append
from _parser import Parser


DEBUG = False


class Label:
    """
    Implements a class to hold the position
    of an undefined jump target in the bytecode.
    """
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return 'Label(name={})'.format(self.name)


def _assemble_codeobject(func_code, label_pos_map, args=[]):
    """
    Assemble a CodeObject.

    Instead of creating a separate class for assembling
    the variable and constants references in CodeObjects,
    we assemble them on the fly.
    """
    code = []
    constants = []
    varnames = []
    for instruction in func_code:
        if isinstance(instruction, Label):
            continue
        elif instruction.opcode == OP_LOAD_CONST:
            if isinstance(instruction.arg, (Pair, String)):
                constants.append(instruction.arg)
                arg = len(constants) - 1
            else:
                arg = find_or_append(constants, instruction.arg)
        elif instruction.opcode in (OP_LOAD_VAR, OP_DEF_VAR, OP_SET_VAR):
            arg = find_or_append(varnames, instruction.arg.value)
        elif instruction.opcode == OP_DEF_FUNC:
            # since CodeObjects are assembled "on the fly",
            # there is no need to recursively assemble them.
            constants.append(instruction.arg)
            arg = len(constants) - 1
        elif instruction.opcode == OP_PROC_CALL:
            arg = instruction.arg
        elif instruction.opcode in (OP_JUMP, OP_JUMP_IF_FALSE):
            arg = label_pos_map[instruction.arg.name]
        elif instruction.opcode in (OP_POP, OP_RETURN):
            arg = None
        else:
            raise CompilerError("Unknown opcode: {}".format(opcode_to_str(instruction.opcode)))
        code.append(Instruction(instruction.opcode, arg))

    return CodeObject(code, args, constants, varnames)


def _assemble_jump_targets(func_code):
    """
    enumerate through the given function code. If a Label is seen,
    map the labels name to its position. Return the mapping of label
    names to positions.
    """
    label_pos_map = {}
    pos = 0
    for instruction in func_code:
        if isinstance(instruction, Label):
            label_pos_map[instruction.name] = pos
        else:
            pos += 1
    return label_pos_map


class CompilerError(Exception):
    """
    Compiler error exception
    """
    pass


class Compiler:
    """
    The implementation of a Scheme compiler.
    """
    def __init__(self, expressions):
        """
        Create a new compiler object.
        """
        self.expressions = expressions
        self._curr_label = 0

    def compile(self):
        """
        The top-level function of this class.
        Returns a compiled CodeObject.
        """
        compiled_expressions = self._compile_expressions(self.expressions)

        # compute jump targets in top-level code object.
        jump_targets = _assemble_jump_targets(compiled_expressions)
        return _assemble_codeobject(compiled_expressions, jump_targets)

    def _instruction(self, opcode, arg=None):
        """
        A helper function for creating Instructions.
        """
        return Instruction(opcode, arg)

    def _instruction_sequence(self, *args):
        """
        A helper function for returning a list of
        instructions.
        """
        return list(flatten(args))

    def _emit_label(self):
        name = 'label_{}'.format(self._curr_label)
        self._curr_label += 1
        return Label(name)

    def _compile(self, expr):
        """
        Compile a single Scheme expression.
        """
        if DEBUG:
            print("DEBUG: expression being executed: {}".format(repr(expr)))
            print("DEBUG: it is an instance of {}\n".format(type(expr)))
        if is_null(expr):
            return self._instruction(OP_LOAD_CONST, expr)
        if is_const(expr):
            return self._instruction(OP_LOAD_CONST, expr)
        elif is_variable(expr):
            return self._instruction(OP_LOAD_VAR, expr)
        elif is_quoted(expr):
            return self._instruction(OP_LOAD_CONST, quoted_text(expr))
        elif is_assignment(expr):
            return self._instruction_sequence(
                self._compile(variable_value(expr)),
                self._instruction(OP_SET_VAR, variable_name(expr))
            )
        elif is_lambda(expr):
            return self._compile_lambda(expr)
        elif is_begin(expr):
            return self._compile_begin(begin_body(expr))
        elif is_definition(expr):
            return self._compile_definition(expr)
        elif is_if(expr):
            return self._compile_if(expr)
        elif is_cond(expr):
            return self._compile(make_ifs_from_cond(cond_clauses(expr)))
        elif is_let(expr):
            return self._compile(make_let_into_lambda(expr))
        elif is_proc_call(expr):
            return self._compile_proc_call(expr)
        else:
            raise CompilerError('Unknown expression to compile: {}'.format(expr))

    def _compile_lambda(self, expr):
        """
        Compile a Scheme lambda expression.
        """
        # check to see if they properly defined the lambda.
        # This includes creating a pair of parenthesis for the
        # parameter list and the body, even if their both empty.
        if expr.second is None:
            raise CompilerError("Invalid definition of lambda")

        args = expand_nested_pairs(lambda_parameters(expr))
        arglist = []

        for arg in args:
            if isinstance(arg, Symbol):
                arglist.append(arg)
            else:
                raise CompilerError("Only symbols are supported in lambda arguments")

        lambda_code = self._instruction_sequence(
            self._compile_begin(lambda_body(expr)),
            self._instruction(OP_RETURN)
        )

        jump_targets = _assemble_jump_targets(lambda_code)
        return self._instruction(
            OP_DEF_FUNC,
            _assemble_codeobject(lambda_code, jump_targets, arglist)
        )

    def _compile_begin(self, expr):
        """
        Compile a list of scheme expressions
        in the from of begin.
        """
        expressions = expand_nested_pairs(expr)
        return self._compile_expressions(expressions)

    def _compile_expressions(self, expressions):
        """
        Compile a list of scheme expressions
        """
        instructions_with_pop = list(self._instruction_sequence(
            self._compile(expr),
            self._instruction(OP_POP)
        ) for expr in expressions)
        flat_instructions = self._instruction_sequence(*instructions_with_pop)
        return flat_instructions[:-1]

    def _compile_definition(self, expr):
        """
        Compile a scheme definition.
        """
        # Check to see if a value is given for
        # the variable definition. If not, raise
        # an error.
        if expr.second.second is None:
            raise CompilerError("Invalid use of define. Requires a value to bind to the variable.")
        value = self._compile(definition_value(expr))
        var = definition_variable(expr)
        # If we are defining a lambda, give it the
        # variable name which it is being defined with.
        if not isinstance(value, list) and isinstance(value.arg, CodeObject):
            value.arg.name = var.value
        return self._instruction_sequence(
            value,
            self._instruction(OP_DEF_VAR, var)
        )

    def _compile_if(self, expr):
        # Check to see if we have a valid define expression. We require a then-branch
        # and else-branch. Any expressions after those are ignored.
        if len(expand_nested_pairs(expr)) < 4:
            raise CompilerError("Invalid use of if. Requires a then-branch and else-branch")

        then_branch_jump = self._emit_label()
        else_branch_jump = self._emit_label()

        return self._instruction_sequence(
            self._compile(if_cond(expr)),
            self._instruction(OP_JUMP_IF_FALSE, then_branch_jump),
            self._compile(if_then(expr)),
            self._instruction(OP_JUMP, else_branch_jump),
            [then_branch_jump],
            self._compile(if_else(expr)),
            [else_branch_jump]
        )

    def _compile_proc_call(self, expr):
        """
        Compile a scheme procedure call. Otherwise
        known as an "operator application".
        """
        args = expand_nested_pairs(procedure_args(expr))
        compiled_args = self._instruction_sequence(*[self._compile(arg) for arg in args])
        compiled_op = self._compile(procedure_op(expr))
        return self._instruction_sequence(
            compiled_args,
            compiled_op,
            self._instruction(OP_PROC_CALL, len(args))
        )


def compile_source(source):
    """
    Helper function for compiling and assembling
    a string containing Scheme source code, into
    a code object.
    """
    expressions = Parser(source).parse()
    return Compiler(expressions).compile()
