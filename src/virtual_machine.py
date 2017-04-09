"""
virtual_machine.py
----------------------------------------

A virtual machine implementation for Scheme.
"""

from sys import stdout
from _builtins import builtin_map, Procedure, check_type
from environment import Environment
from bytecode import (OP_LOAD_CONST, OP_LOAD_VAR, OP_SET_VAR,
                      OP_DEF_VAR, OP_DEF_FUNC, OP_PROC_CALL, OP_RETURN,
                      OP_POP, OP_JUMP_IF_FALSE, OP_JUMP, opcode_to_str)
from expressions import Boolean, String
from compiler import compile_source


DEBUG = False


class Closure:
    """
    Represents a user-defined function(or closure),
    with the current global environment.
    """

    def __init__(self, codeobject, environment):
        self.codeobject = codeobject
        self.environment = environment

    def __repr__(self):
        return '#<Closure {}>'.format(self.codeobject.name)


class Frame:
    """
    Represents a function-call on the virtual machine
    call stack.
    """

    def __init__(self, codeobject, environment):
        self.codeobject = codeobject
        self.environment = environment
        self.stack = []
        self.instr_pointer = 0

    def __repr__(self):
        """
        Print current state of Frame(for debugging).
        """
        _repr = '\nFrame {}:\n'.format(self.codeobject.name)
        _repr += '\tinstr_pointer: ' + repr(self.instr_pointer) + '\n'
        _repr += '\tstack: ' + repr(self.stack) + '\n'
        return _repr


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
        self.return_value = None
        self.output_stream = output_stream

    def run_code(self, code):
        """
        Execute the code object given, and return the value.
        """
        frame = self._make_frame(code)
        self._run_frame(frame)

    def _make_frame(self, code, arg_bindings=None, environment=None):
        arg_bindings = arg_bindings or {}
        environment = environment or self.frame or self._make_standard_env()
        return Frame(code,  Environment(arg_bindings, environment))

    def _make_standard_env(self):
        """
        Create a standard Scheme namespace.
        """
        environment = {}
        for name, proc in builtin_map.items():
            environment[name] = Procedure(name, proc)
        # These builtins require state in the VM, so they could not
        # have been defined in _builtins.py.
        environment['print'] = Procedure('print', self._builtin_print)
        environment['load'] = Procedure('load', self._builtin_load)
        return Environment(environment)

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
        Run the code inside of the current frames code object, until
        it returns(something).
        """
        self._push_frame(frame)
        while True:
            instruction = self._get_next_instruction()

            # debug the vm by printing out the data stack,
            # frame stack, and current instruction(with the
            # argument).
            if DEBUG:
                print('current instruction:', instruction)
                print('frame stack:', self.frames)
                print('return value of previous frame:', self.return_value)
                print('----------------------------------')

            if instruction is not None:
                why = self._run_instruction(instruction)
                if why:
                    break
            else:
                break
        self._pop_frame()
        return self.return_value

    def _run_instruction(self, instruction):
        codeobject = self.frame.codeobject
        environment = self.frame.environment

        if instruction.opcode == OP_LOAD_CONST:
            const = codeobject.constants[instruction.arg]
            self._push(const)
        elif instruction.opcode == OP_LOAD_VAR:
            varname = codeobject.varnames[instruction.arg]
            val = environment.lookup_var(varname)
            self._push(val)
        elif instruction.opcode == OP_SET_VAR:
            varname = codeobject.varnames[instruction.arg]
            val = self._pop()
            environment.set_var(varname, val)
        elif instruction.opcode == OP_DEF_VAR:
            varname = codeobject.varnames[instruction.arg]
            val = self._pop()
            environment.define_var(varname, val)
        elif instruction.opcode == OP_DEF_FUNC:
            func_codeobject = codeobject.constants[instruction.arg]
            closure = Closure(func_codeobject, environment)
            self._push(closure)
        elif instruction.opcode == OP_PROC_CALL:
            proc = self._pop()
            args = [self._pop() for _ in range(instruction.arg)]
            args.reverse()

            if isinstance(proc, Procedure):
                retval = proc.apply(*args)
                self._push(retval)
            elif isinstance(proc, Closure):
                # Check if the correct number of arguments are passed in.
                if len(proc.codeobject.args) != len(args):
                    raise VirtualMachineError(
                        "procedure \"{}\" expected {} argument(s), but got {} argument(s) instead.".format(
                            proc.codeobject.name, len(proc.codeobject.args), len(args)
                        ))

                # we need to bind the values passed to this closure, to the argument
                # names. This way, the closure can properly references the parameters used
                # inside of its body.
                arg_bindings = {}
                for pos, arg in enumerate(proc.codeobject.args):
                    arg_bindings[arg.value] = args[pos]

                frame = self._make_frame(proc.codeobject, arg_bindings, proc.environment)
                retval = self._run_frame(frame)
                self._push(retval)
            else:
                raise VirtualMachineError("{} is not a function.".format(
                    proc.value if hasattr(proc, 'value') else proc)
                )
        elif instruction.opcode == OP_JUMP_IF_FALSE:
            cond = self._pop()
            if isinstance(cond, Boolean) and cond.value is False:
                self.frame.instr_pointer = instruction.arg
        elif instruction.opcode == OP_JUMP:
            self.frame.instr_pointer = instruction.arg
        elif instruction.opcode == OP_RETURN:
            # make sure the current frame actual has a
            # return value.
            if self.frame.stack:
                self.return_value = self._pop()
            return 'return'
        elif instruction.opcode == OP_POP:
            if self.frame.stack:
                self._pop()
        else:
            raise VirtualMachineError("Unknown bytecode: {}".format(opcode_to_str(instruction.opcode)))

    def _get_next_instruction(self):
        if self.frame.instr_pointer >= len(self.frame.codeobject.code):
            return None
        else:
            instruction = self.frame.codeobject.code[self.frame.instr_pointer]
            self.frame.instr_pointer += 1
            return instruction

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

    def _builtin_print(self, *args):
        self.output_stream.write(str(args[0]) + '\n')
        return '<#undef>'

    def _builtin_load(self, string):
        check_type(String, string, "Filename must be a string")
        try:
            with open(string.value) as file:
                source = file.read()
        except FileNotFoundError:
            raise VirtualMachineError('File "{}" could not be located.'.format(string.value))

        # once we have compiled our "imported" source file, execute it.
        co = compile_source(source)
        frame = self._make_frame(co)
        self._run_frame(frame)

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
        if self.expr_stack:
            return self.expr_stack[-1]
        else:
            return '<#undef>'

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
            instruction = self._get_next_instruction()
            if instruction is not None:
                why = self._run_instruction(instruction)
                if why:
                    break
            else:
                break
        self._pop_frame()
        return self.return_value
