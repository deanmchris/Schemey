"""
environment.py
----------------------------------------

The internal implementation of a Scheme environment.
----------------------------------------

Algerbrex(c1dea2n@gmail.com)

All code in this module is
public domain.

Last modified: February 5 2017
"""


class Undefined(Exception):
    pass


class Environment:
    """
    The implementation of scheme environment. An environment
    holds variables -> value hashes and has helper functions
    for check if a variable is defined, defining variables, and
    setting variables.
    """
    def __init__(self, binding, parent_env=None):
        """
        Create a new Environment with the given binding(a variable -> value)
        dictionary.

        Each environment is linked together via a reference. All variables are define
        in the current environment, but subsequent parent directories may be searched
        for a variable definition.
        """
        self.binding = {}
        self.parent_env = parent_env
        self.binding.update(binding)

    def lookup_var(self, varname):
        """
        Check to see if a variable with the
        given name is defined. Search up to the
        top-most parent environment. if the variable
        is define, return the value. Otherwise return
        False.
        """
        if varname in self.binding:
            return self.binding[varname]
        elif self.parent_env is not None:
            return self.parent_env.lookup_var(varname)
        else:
            raise Undefined('variable "{}" is undefined'.format(varname))

    def define_var(self, varname, value):
        """
        Define a variable in this environment
        with the given value.
        """
        self.binding[varname] = value

    def set_var(self, varname, value):
        """
        Set(re-define) a variable in this environment
        with the given value.
        """
        if varname in self.binding:
            self.binding[varname] = value
        elif self.parent_env is not None:
            return self.parent_env.set_var(varname, value)
        else:
            raise Undefined('variable "{}" is undefined'.format(varname))
