"""
compiler.py
----------------------------------------

This module contains the implementation of the
Scheme compiler for Schemey. It takes in one
or more expressions(a list of Pair objects), and generates
a code object ready for serialization and/or direct
execution by the virtual machine.
----------------------------------------

Algerbrex(c1dea2n@gmail.com)

All code in this module is
public domain.

Last modified: February 5 2017
"""

from bytecode import *
from expressions import *
from utils import flatten, find_or_append
from _parser import Parser

DEBUG = False


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

    def compile(self):
        """
        The top-level function of this class.
        Returns a compiled CodeObject.
        """
        compiled_expressions = self._compile_expressions(self.expressions)
        return self._assemble_codeobject(compiled_expressions, args=[])

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
        return self._instruction(
            OP_DEF_FUNC,
            self._assemble_codeobject(lambda_code, arglist)
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

    def _assemble_codeobject(self, func_code, args):
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
            if instruction.opcode == OP_LOAD_CONST:
                if isinstance(instruction.arg, Pair):
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
            elif instruction.opcode in (OP_POP, OP_RETURN):
                arg = None
            else:
                raise CompilerError("Unknown opcode: {}".format(instruction.opcode))
            code.append(Instruction(instruction.opcode, arg))

        return CodeObject(code, args, constants, varnames)


def compile_source(source):
    """
    Helper function for compiling and assembling
    a string containing Scheme source code, into
    a code object.
    """
    expressions = Parser(source).parse()
    return Compiler(expressions).compile()
