"""
utils.py
----------------------------------------

This module provides a generally utility
functions for use in various stages of the
interpreter.

"""
from inspect import signature
import struct


def find_or_append(seq, item):
    """
    Return the index of `item` in `seq`. If item is not in `seq`,
    append `item` to `seq` and return the index of `item`.
    """
    try:
        return seq.index(item)
    except ValueError:
        seq.append(item)
        return len(seq) - 1


def flatten(seq):
    """
    Given a sequence(list or tuple), flatten
    the sequence into a one dimensional list.
    """
    for el in seq:
        if isinstance(el, (list, tuple)):
            yield from flatten(el)
        else:
            yield el


def pack_integer(value):
    """
    Pack an integer value into 32-bits,
    little endian form.
    """
    return struct.pack('<I', value)


def unpack_integer(value):
    """
    Unpack an integer from byte form, to
    its original form.
    """
    return struct.unpack('<I', value)[0]


def pack_string(value):
    """
    Pack a string into byte format. Return
    the length of the string and the encoded
    string value, in bytes.
    """
    encoded_value = value.encode('utf-16')
    return pack_integer(len(encoded_value)) + encoded_value


def unpack_string(value):
    """
    Unpack a string from byte format,
    to its original form.
    """
    return value.decode('utf-16')


class Stream:
    """
    A simple class implementing byte iterator.
    """
    def __init__(self, stream):
        self.stream = stream
        self.counter = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.counter >= len(self.stream):
            raise StopIteration
        else:
            self.counter += 1
            return self.stream[self.counter - 1:self.counter]

    def read(self, nbytes):
        """
        Read `nbytes` bytes from the iterator.
        """
        return b''.join(next(self) for _ in range(nbytes))

    def get_curr_byte(self):
        """
        Get the byte at the index `self.counter` is currently at.
        """
        if self.counter >= len(self.stream):
            return b''
        return bytes([self.stream[self.counter]])

    def advance(self):
        """
        Advance `self.counter`.
        """
        self.counter += 1


def get_number_of_params(func_obj):
    """
    Given a function object, get the number of arugments the function
    takes. return 'postional' if the first parameter is `*args`.
    """
    params = list(signature(func_obj).parameters.values())
    first_param = params[0]
    if first_param.kind == first_param.VAR_POSITIONAL:
        return 'positional'
    else:
        return len(params)
