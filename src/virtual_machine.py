"""
virtual_machine.py
----------------------------------------

A virtual machine implementation for Scheme.
----------------------------------------

Algerbrex(c1dea2n@gmail.com)

All code in this module is
public domain.

Last modified: February 5 2017
"""

from sys import stdout
from _builtins import builtin_map, Procedure
from environment import Environment
from bytecode import (OP_LOAD_CONST, OP_LOAD_VAR, OP_SET_VAR,
                      OP_DEF_VAR, OP_DEF_FUNC, OP_PROC_CALL, OP_RETURN, OP_POP,
                      opcode_to_str)


class Closure:
    """
    Represents a user-defined function(or closure),
    with the current global environment.
    """

    def __init__(self, codeobject, environment):
        self.codeobject = codeobject
        self.environment = environment

    def __repr__(self):
        return '#<Closure>'


class Frame:
    """
    Represents a function-call on the virtual machine
    call stack.
    """

    def __init__(self, codeobject, environment, prev_frame):
        self.codeobject = codeobject
        self.environment = environment
        self.stack = []
        self.instr_pointer = 0


class VirtualMachineError(Exception):
    """
    Virtual machine error exception.
    """
    pass


class VirtualMachine:
    """
    Implementation of SchemeyVM.
    """

    def __init__(self, output_stream=stdout):
        self.frames = []
        self.frame = None
        self.output_stream = output_stream

    def run_code(self, code):
        """
        Execute the code object given, and return the value.
        """
        frame = self._make_frame(code)
        self._run_frame(frame)

    def _make_standard_env(self):
        """
        Create a standard Scheme namespace.
        """
        environment = {}
        for name, proc in builtin_map.items():
            environment[name] = Procedure(name, proc)
        # This builtin requires state in the VM, so it could not
        # have been defined in builtins.
        environment['print'] = Procedure('print', self._print)
        return Environment(environment)

    def _make_frame(self, code, args={}):
        """
        Given a code object, and possible arguments,
        create a Frame object.
        """
        if self.frames:
            environment = self.frame.environment
        else:
            environment = self._make_standard_env()
        environment.binding.update(args)
        frame = Frame(code, environment, self.frame)
        return frame

    def _push_frame(self, frame):
        """
        Push a frame to the stack.
        """
        self.frames.append(frame)
        self.frame = frame
        self.retval = None

    def _pop_frame(self):
        """
        Pop a frame from the stack, and set the current frame
        equal to the frame before it.
        """
        self.frames.pop()
        self.frame = self.frames[-1] if self.frames else None

    def _run_frame(self, frame):
        """
        Execute the current frame until it returns.
        """
        self._push_frame(frame)
        while True:
            why = self._dispatch()
            if not self.frame:
                if not self.frames:
                    return
                else:
                    raise VirtualMachineError("Execution of frame unexpectedly ended: {}".format(frame.codeobject))
            if why is not None:
                break
        self._pop_frame()

    def _dispatch(self):
        """
        Run the code inside of the current frames code object, until
        it returns(something).
        """
        f = self.frame
        if f.instr_pointer >= len(f.codeobject.code):
            return 'done'
        environment = f.environment
        bytecode = f.codeobject.code[f.instr_pointer]
        f.instr_pointer += 1

        if bytecode.opcode == OP_LOAD_CONST:
            self._push(f.codeobject.constants[bytecode.arg])
        elif bytecode.opcode == OP_LOAD_VAR:
            var = environment.lookup_var(f.codeobject.varnames[bytecode.arg])
            self._push(var)
        elif bytecode.opcode == OP_SET_VAR:
            val = self._pop()
            environment.set_var(f.codeobject.varnames[bytecode.arg], val)
        elif bytecode.opcode == OP_DEF_VAR:
            val = self._pop()
            environment.define_var(f.codeobject.varnames[bytecode.arg], val)
        elif bytecode.opcode == OP_DEF_FUNC:
            closure = Closure(f.codeobject.constants[bytecode.arg], environment)
            self._push(closure)
        elif bytecode.opcode == OP_PROC_CALL:
            proc = self._pop()
            args = [self._pop() for _ in range(bytecode.arg)]
            if isinstance(proc, Procedure):
                retval = proc.apply(*reversed(args))
                self._push(retval)
            elif isinstance(proc, Closure):
                # Check if the correct number of arguments is passed in.
                if len(proc.codeobject.args) != len(args):
                    raise VirtualMachineError(
                        "procedure \"{}\" expected {} argument(s), but got {} argument(s) instead.".format(
                            proc.codeobject.name, len(proc.codeobject.args), len(args)
                        ))
                # we need to bind the values passed to this closure, to the argument
                # names. This way, the closure can properly references the parameters used
                # inside of its body.
                vals_bound_to_args = {argname.value: val for argname in proc.codeobject.args for val in args}
                frame = self._make_frame(proc.codeobject, vals_bound_to_args)
                self._run_frame(frame)
            else:
                # Sometimes `proc` is not a Procedure,
                # but a Pair. Deal with those cases, and
                # find the correct value to display in the
                # error message.
                if hasattr(proc, 'value'):
                    value = proc.value
                else:
                    value = proc
                raise VirtualMachineError("\"{}\" is not a function. Expected a function.".format(value))
        elif bytecode.opcode == OP_RETURN:
            retval = self._pop()
            self._pop_frame()
            self._push(retval)
        elif bytecode.opcode == OP_POP:
            if self.frame.stack:
                self._pop()
        else:
            raise VirtualMachineError("Unknown opcode: {}".format(opcode_to_str(bytecode.opcode)))

    def _top(self):
        """
        Get the top value of the value stack.
        """
        return self.frame.stack[-1]

    def _pop(self):
        """
        Pop a value from the value stack.
        """
        return self.frame.stack.pop()

    def _push(self, *vals):
        """
        Push one or more values to the value stack.
        """
        self.frame.stack.extend(vals)

    # -------------------------------------------------------#
    # builtin procedures which require access to the VM's   #
    # state                                                 #
    # ------------------------------------------------------#

    def _print(self, *args):
        self.output_stream.write(str(args[0]) + '\n')
        return '<#undef>'


class ReplVM(VirtualMachine):
    """
    A subclass of VirtualMachine. This subclass simply implements
    a way to return the last expression on the last frames stack
    to implement a repl.
    """

    def __init__(self):
        super(ReplVM, self).__init__()
        self.expr_stack = []
        self.last_frame = []

    def run_code(self, code):
        """
        Since this virtual machine is used to implement a repl,
        we need to grab the last value from self.expr_stack and
        return it. That will be the result displayed in the repl.
        """
        frame = self._make_frame(code)
        self._run_frame(frame)
        return self.expr_stack[-1]

    def update_env(self):
        """
        Reset the virtual machines internals.
        """
        curr_frame = {}
        for prev_frame in self.last_frame:
            curr_frame.update(prev_frame.environment.binding)
        return curr_frame

    def _run_frame(self, frame):
        """
        Execute the current frame until it returns.
        """
        self.last_frame.append(frame)
        frame.environment.binding = self.update_env()
        self._push_frame(frame)
        while True:
            self.expr_stack.extend(self.frame.stack)
            why = self._dispatch()
            if not self.frame:
                if not self.frames:
                    return
                else:
                    raise VirtualMachineError("Execution of frame unexpectedly ended: {}".format(frame.codeobject))
            if why is not None:
                break
        self._pop_frame()
