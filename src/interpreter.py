"""
interpreter.py
--------------
An interpreter implementation for Scehemy.
"""

from sys import stdout, setrecursionlimit
from ._builtins import builtin_map, Procedure, check_type
from .environment import Environment
from .expressions import *
from ._parser import Parser


DEBUG = False


class Closure:
    def __init__(self, args, body, env, name):
        self.args = args
        self.body = body
        self.env = env
        self.name = name

    def __repr__(self):
        return '#<Closure {}>'.format(self.name)


class InterpreterError(Exception):
   pass


class Interpreter:
    def __init__(self, output_stream):
        self.output_stream = output_stream
        self.environment = self._make_standard_env()

    def _make_standard_env(self):
        environment = {}
        for name, proc in builtin_map.items():
            environment[name] = Procedure(name, proc)
        # These builtins require state in the VM, so they could not
        # have been defined in _builtins.py.
        environment['print'] = Procedure('print', self._builtin_print)
        environment['load'] = Procedure('load', self._builtin_load)
        return Environment(environment)

    def run(self, expr):
        return self._eval(expr)

    def _eval(self, expr):
        if DEBUG:
            print("DEBUG: expression being executed: {}".format(repr(expr)))
            print("DEBUG: it is an instance of {}\n".format(type(expr)))
        if is_const(expr) or is_null(expr):
            return expr
        elif is_variable(expr):
            return self.environment.lookup_var(expr.value)
        elif is_quoted(expr):
            return quoted_text(expr)
        elif is_assignment(expr):
            return self._eval_assignment(expr)
        elif is_lambda(expr):
            return self._eval_lambda(expr)
        elif is_begin(expr):
            return self._eval_begin(begin_body(expr))
        elif is_definition(expr):
            return self._eval_definition(expr)
        elif is_if(expr):
            return self._eval_if(expr)    
        elif is_cond(expr):
            return self._eval(make_ifs_from_cond(cond_clauses(expr)))
        elif is_let(expr):
            return self._eval(make_let_into_lambda(expr))
        elif is_proc_call(expr):
            return self._eval_proc_call(expr)
        else:
            raise InterpreterError('Unknown expression to interpret: {}'.format(expr))

    def _eval_assignment(self, expr):
        val = self._eval(variable_value(expr))
        name = variable_name(expr)
        self.environment.set_var(name.value, val)

    def _eval_lambda(self, expr):
        args = expand_nested_pairs(lambda_parameters(expr))
        env = self.environment
        closure = Closure(args, lambda_body(expr), env, '')
        return closure

    def _eval_begin(self, expr):
        return self._eval_sequence(expr)

    def _eval_definition(self, expr):
        val = self._eval(definition_value(expr))
        var = definition_variable(expr)
        if isinstance(val, Closure):
            val.name = var.value if var.value else '<anonymous>'
        self.environment.define_var(var.value, val)

    def _eval_if(self, expr):
        condition = self._eval(if_cond(expr)) 
        if isinstance(condition, Boolean) and condition.value == False:
            # Do we have an optional else statement.
            if len(expand_nested_pairs(expr)) >= 4:
                return self._eval(if_else(expr))
            else:
                return None
        else:
            return self._eval(if_then(expr))

    def _eval_proc_call(self, expr):
        args = expand_nested_pairs(procedure_args(expr))
        args = [self._eval(arg) for arg in args]
  
        name = procedure_op(expr)
        proc = self._eval(name)

        if DEBUG: print('DEBUG: Applying procedure {}'.format(name))
        if DEBUG: print('DEBUG:     With arguments {}'.format(args))

        if isinstance(proc, Procedure):
            if DEBUG: print('DEBUG: Applying builtin procedure with arguments {}\n'.format(args))

            retval = proc.apply(*args)
            return retval
        elif isinstance(proc, Closure):
            if DEBUG: print('DEBUG: Applying closure with arguments {}'.format(args))
            if DEBUG: print('DEBUG:     With parameters {}\n'.format(proc.args))

            if len(proc.args) != len(args):
                raise InterpreterError(
                    "procedure \"{}\" expected {} argument(s), but got {} argument(s) instead.".format(
                        proc.name, len(proc.args), len(args)
                    ))
            arg_bindings = {}
            for pos, arg in enumerate(proc.args):
                arg_bindings[arg.value] = args[pos]

            curr_environment = self.environment
            self.environment = Environment(arg_bindings, proc.env)

            retval = self._eval_sequence(proc.body)
            self.environment = curr_environment
            return retval
        else:
            type_ = proc.value if hasattr(proc, 'value') else proc
            raise InterpreterError('unknown type in procedure call: {}'.format(type_))
            
    def _eval_sequence(self, expressions):
        first = self._eval(expressions.first)
        if isinstance(expressions.second, Nil):
            return first
        else:
            return self._eval_sequence(expressions.second)

    def _builtin_print(self, *args):
        self.output_stream.write(str(args[0]) + '\n')

    def _builtin_load(self, string):
        check_type(String, string, "Filename must be a string")
        try:
            with open(string.value) as file:
                source = file.read()
        except FileNotFoundError:
            raise InterpreterError('File "{}" could not be located.'.format(string.value))

        # once we have compiled our "imported" source file, execute it.
        exprs = Parser(source).parse()
        for expr in exprs:
            self._eval(expr)


def interpret_expressions(code_str, output_stream=stdout):
    exprs = Parser(code_str).parse()
    interp = Interpreter(output_stream)

    setrecursionlimit(500000)

    for expr in exprs:
        interp.run(expr)

