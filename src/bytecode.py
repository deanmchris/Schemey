"""
bytecode.py
----------------------------------------

Implementation of bytecode instructions. Also
includes the implementation of CodeObjects objects,
Instruction objects, and the serializer and deserializer
for the CodeObjects.

"""

from utils import pack_integer, unpack_integer, pack_string, unpack_string, Stream
from expressions import Pair, Symbol, Number, Boolean, Nil, String

OP_LOAD_CONST = 0x00
OP_LOAD_VAR = 0x01
OP_SET_VAR = 0x02
OP_DEF_VAR = 0x03
OP_DEF_FUNC = 0x04
OP_PROC_CALL = 0x05
OP_JUMP_IF_FALSE = 0x06
OP_JUMP = 0x07
OP_RETURN = 0x08
OP_POP = 0x09


_opcode_to_str_map = {
    0x00: 'OP_LOAD_CONST',
    0x01: 'OP_LOAD_VAR',
    0x02: 'OP_SET_VAR ',
    0x03: 'OP_DEF_VAR ',
    0x04: 'OP_DEF_FUNC',
    0x05: 'OP_PROC_CALL',
    0x06: 'OP_JUMP_IF_FALSE',
    0x07: 'OP_JUMP',
    0x08: 'OP_RETURN',
    0x09: 'OP_POP '
}


def opcode_to_str(opcode):
    return _opcode_to_str_map[opcode]


class Instruction:
    """
    A structure for holding the operation code and optional
    argument for each instruction generated.
    """

    def __init__(self, opcode, arg):
        self.opcode = opcode
        self.arg = arg

    def __repr__(self):
        if self.arg is None:
            return '{:<24}'.format(opcode_to_str(self.opcode))
        else:
            return '{:<24}{}'.format(opcode_to_str(self.opcode), self.arg)


class CodeObject:
    """
    Represents a compiled Scheme procedure. A code object is ready
    for serialization and/or direct execution by the virtual machine.

    name:
        The procedures name. Used for debugging.

    code:
        A list of Instruction objects containing the
        bytecode instructions.

    args:
        A list of arguments to the procedure.

    constants:
        A list of constants referenced in the procedure. The constants can either be
        a Scheme expression - as implemented in expressions.py - or a CodeObject itself.

    varnames:
        A list of variable names referenced in the procedure.
    """

    def __init__(self, code, args, constants, varnames, name=''):
        self.name = name or 'Anonymous procedure'
        self.code = code
        self.args = args
        self.constants = constants
        self.varnames = varnames

    def __repr__(self, indent=0):
        repr_ = ''
        prefix = ' ' * indent

        repr_ += prefix + '---------------\n'
        repr_ += prefix + 'Procedure: ' + self.name + '\n'
        repr_ += prefix + 'Arguments: ' + str(self.args) + '\n'
        repr_ += prefix + 'Variables referenced: ' + str(self.varnames) + '\n'

        constants = []
        for constant in self.constants:
            if isinstance(constant, CodeObject):
                constants.append('\n' + constant.__repr__(indent + 4))
            else:
                constants.append(('\n    ' + prefix) + repr(constant))
        repr_ += prefix + 'Constants referenced: ' + ''.join(constants) + '\n'

        formatted_code = self._format_code(prefix=prefix)
        repr_ += prefix + 'Code: ' + ''.join(formatted_code) + '\n'
        repr_ += prefix + '---------------\n'
        return repr_

    def _format_code(self, prefix):
        """
        Iterate over the opcodes of the class, and
        "pretty-format" each one.
        """
        formatted_code = []
        for pos, instruction in enumerate(self.code):
            instr_repr = ('\n    ' + prefix + '({}) '.format(pos)) + repr(instruction)

            if instruction.opcode == OP_LOAD_CONST:
                instr_repr += ' [{}]'.format(self.constants[instruction.arg])
            elif instruction.opcode == OP_LOAD_VAR:
                instr_repr += ' [{}]'.format(self.varnames[instruction.arg])
            elif instruction.opcode == OP_SET_VAR:
                instr_repr += ' [{}]'.format(self.varnames[instruction.arg])
            elif instruction.opcode == OP_DEF_VAR:
                instr_repr += ' [{}]'.format(self.varnames[instruction.arg])
            elif instruction.opcode == OP_DEF_FUNC:
                instr_repr += ' [{}]'.format(self.constants[instruction.arg].name)
            elif instruction.opcode == OP_PROC_CALL:
                instr_repr += ' [no args]'
            elif instruction.opcode == OP_JUMP_IF_FALSE:
                instr_repr += ' [{}]'.format(instruction.arg)
            elif instruction.opcode == OP_JUMP:
                instr_repr += ' [{}]'.format(instruction.arg)
            elif instruction.opcode == OP_RETURN:
                instr_repr += ' [no args]'
            elif instruction.opcode == OP_POP:
                instr_repr += ' [no args]'

            formatted_code.append(instr_repr)

        return formatted_code


"""
What follows is a custom implementation of a simple serialization
API for CodeObjects. The design is very simple and easy to understand, and is
based of off CPython's  and Bobscheme's marshaling API.

Each serialised object is prefixed with a "type" byte which tells the objects
type, and then the bytecode format of each object.

I've tried to make my code readable, simple, and easy to understand. So
take a look at the code below!
"""

TYPE_CODEOBJECT = b'C'
TYPE_INSTRUCTION = b'I'
TYPE_PAIR = b'P'
TYPE_BOOLEAN = b'B'
TYPE_NUMBER = b'N'
TYPE_SYMBOL = b'S'
TYPE_SEQUENCE = b'['
TYPE_STRING = b's'
TYPE_PY_STRING = b'p'
TYPE_NIL = b'n'

MAGIC_CONSTANT = 0x01A


class SerializationError(Exception):
    """
    Serialization error exception.
    """
    pass


class Serializer:
    """
    A custom implementation of a serializer for CodeObjects.
    This is based off of the CPython implementation.
    """

    def __init__(self, codeobject):
        self.co = codeobject

    def _dispatch(self, value):
        """
        Given a value, determine its type,
        and call the corresponding serialization
        method.
        """
        if isinstance(value, CodeObject):
            return self._serialize_codeobject(value)
        elif isinstance(value, Instruction):
            return self._serialize_instruction(value)
        elif isinstance(value, Pair):
            return self._serialize_pair(value)
        elif isinstance(value, Boolean):
            return self._serialize_boolean(value)
        elif isinstance(value, Number):
            return self._serialize_number(value)
        elif isinstance(value, Symbol):
            return self._serialize_symbol(value)
        elif isinstance(value, str):
            return self._serialize_py_string(value)
        elif isinstance(value, String):
            return self._serialize_string(value)
        elif isinstance(value, Nil):
            return self._serialize_nil(value)
        else:
            raise SerializationError("Unknown value of type: {}".format(type(value)))

    def serialize(self):
        """
        The top-level function of this class. Call this
        method to serialize the code object given in the
        constructor.
        """
        serialized_codeobject = self._serialize_codeobject()
        return pack_integer(MAGIC_CONSTANT) + serialized_codeobject

    def _serialize_codeobject(self, value=None):
        """
        Serialize a CodeObject.
        """
        co = value or self.co
        stream = TYPE_CODEOBJECT
        stream += self._serialize_py_string(co.name)
        stream += self._serialize_sequence(co.args)
        stream += self._serialize_sequence(co.code)
        stream += self._serialize_sequence(co.constants)
        stream += self._serialize_sequence(co.varnames)
        return stream

    def _serialize_instruction(self, value):
        """
        Serialize an Instruction object.
        """
        arg = value.arg or 0
        return TYPE_INSTRUCTION + pack_integer(value.opcode) + pack_integer(arg)

    def _serialize_pair(self, value):
        """
        Serialize a Pair object.
        """
        return TYPE_PAIR + self._serialize_object(value.first) + \
               self._serialize_object(value.second)

    def _serialize_boolean(self, value):
        """
        Serialize a Boolean object.
        """
        return TYPE_BOOLEAN + pack_integer(value.value)

    def _serialize_number(self, value):
        """
        Serialize a Number object.
        """
        return TYPE_NUMBER + pack_integer(value.value)

    def _serialize_symbol(self, value):
        """
        Serialize a Symbol object.
        """
        return TYPE_SYMBOL + pack_string(value.value)

    def _serialize_sequence(self, value):
        """
        Serialize a (Python)list of objects. This is similar to
        serializing strings or Symbols, with the difference being
        that we record the actual Python lists length, and not its
        bytecode form.
        """
        stream = b''.join(self._serialize_object(el) for el in value)
        return TYPE_SEQUENCE + pack_integer(len(value)) + stream

    def _serialize_py_string(self, value):
        """
        Serialize a Python string object.
        """
        return TYPE_PY_STRING + pack_string(value)

    def _serialize_string(self, value):
        """
        Serialize a Scheme string object.
        """
        return TYPE_STRING + pack_string(value.value)

    def _serialize_nil(self, value):
        """
        Serialize None.
        """
        # Nil represents nothingness. We only need to return the tag.
        return TYPE_NIL

    def _serialize_object(self, value):
        """
        Serialize a generic object.
        """
        return self._dispatch(value)


class DeserializationError(Exception):
    """
    Deserialization error exception.
    """
    pass


class Deserializer:
    """
    A class to deserialize a serialized code object.
    """

    def __init__(self, bytecode):
        self.stream = Stream(bytecode)

    def deserialize(self):
        """
        Using the bytecode stream given in the constructor,
        deserialize it into a CodeObject.
        """
        magic_const = unpack_integer(self.stream.read(4))
        if magic_const != MAGIC_CONSTANT:
            raise DeserializationError("Magic constant does not match")
        return self._deserialize_codeobject()

    def _match(self, obj_type, msg=''):
        """
        Check if the current byte in our Stream, is equal to `obj_type`.
        """
        if not bytes(self.stream.get_curr_byte()) == obj_type:
            raise DeserializationError("Expected object with type: {}".format(obj_type) if not msg else msg)
        else:
            self.stream.advance()

    def _dispatch(self, obj_type):
        """
        Given an objects "tag" type,
        dispatch the corresponding
        deserialization method. If none
        match the "tag" raise an error.
        """
        if obj_type == TYPE_CODEOBJECT:
            return self._deserialize_codeobject()
        elif obj_type == TYPE_INSTRUCTION:
            return self._deserialize_instruction()
        elif obj_type == TYPE_PAIR:
            return self._deserialize_pair()
        elif obj_type == TYPE_BOOLEAN:
            return self._deserialize_boolean()
        elif obj_type == TYPE_NUMBER:
            return self._deserialize_number()
        elif obj_type == TYPE_SYMBOL:
            return self._deserialize_symbol()
        elif obj_type == TYPE_PY_STRING:
            return self._deserialize_py_string()
        elif obj_type == TYPE_STRING:
            return self._deserialize_string()
        elif obj_type == TYPE_NIL:
            return self._deserialize_nil()
        else:
            raise DeserializationError("Unknown object type: {}".format(obj_type))

    def _deserialize_codeobject(self):
        """
        Deserialize a code object.
        """
        self._match(TYPE_CODEOBJECT, "Top-level object is not a code object.")
        co = CodeObject([], [], [], [])
        co.name = self._deserialize_py_string()
        co.args = self._deserialize_sequence()
        co.code = self._deserialize_sequence()
        co.constants = self._deserialize_sequence()
        co.varnames = self._deserialize_sequence()
        return co

    def _deserialize_instruction(self):
        """
        Deserialize an instruction.
        """
        self._match(TYPE_INSTRUCTION)
        opcode = unpack_integer(self.stream.read(4))
        arg = unpack_integer(self.stream.read(4))
        return Instruction(opcode, arg)

    def _deserialize_pair(self):
        self._match(TYPE_PAIR)
        first = self._deserialize_object()
        second = self._deserialize_object()
        return Pair(first, second)

    def _deserialize_boolean(self):
        """
        Deserialize a CodeObject.
        """
        self._match(TYPE_BOOLEAN)
        return Boolean(unpack_integer(self.stream.read(4)))

    def _deserialize_number(self):
        """
        Deserialize a number.
        """
        self._match(TYPE_NUMBER)
        return Number(unpack_integer(self.stream.read(4)))

    def _deserialize_symbol(self):
        """
        Deserialize a symbol.
        """
        self._match(TYPE_SYMBOL)
        str_len = unpack_integer(self.stream.read(4))
        return Symbol(unpack_string(self.stream.read(str_len)))

    def _deserialize_sequence(self):
        """
        Deserialize a sequence.
        """
        self._match(TYPE_SEQUENCE)
        seq_len = unpack_integer(self.stream.read(4))
        return [self._deserialize_object() for _ in range(seq_len)]

    def _deserialize_py_string(self):
        """
        Deserialize a Python string.
        """
        self._match(TYPE_PY_STRING)
        str_len = unpack_integer(self.stream.read(4))
        return unpack_string(self.stream.read(str_len))

    def _deserialize_string(self):
        self._match(TYPE_STRING)
        str_len = unpack_integer(self.stream.read(4))
        return String(unpack_string(self.stream.read(str_len)))

    def _deserialize_nil(self):
        """
        Deserialize None.
        """
        self._match(TYPE_NIL)
        return Nil()

    def _deserialize_object(self):
        """
        Deserialize a generic object.
        """
        return self._dispatch(self.stream.get_curr_byte())


def serialize(codeobject):
    """
    A convince function for serializing code objects.
    """
    bytecode = Serializer(codeobject).serialize()
    return bytecode


def deserialize(bytecode):
    """
    A convince function for deserializing code objects.
    """
    codeobject = Deserializer(bytecode).deserialize()
    return codeobject
