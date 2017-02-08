"""
lexer.py
----------------------------------------

A simple lexer based upon the "maximal munch" rule.
Because of this, the lexer is not generic and must
be created anew for each specific language.

"""

from collections import namedtuple
from _builtins import builtin_map

ADDITIONAL_BUILTIN_CHARS = {'?', '!', '.'}
GARBAGE_CHARS = {';', ' ', '\n', '\t', '\r'}
TRUE_OR_FALSE_CHARS = {'t', 'f'}
ADD_OR_SUB_CHARS = {'+', '-'}

# Sometimes we need to return the current position
# the lexer is on to raise an appropriate error. That
# is what this class holds. Whenever there is an error,
# an instance is returned to the parser.
Error = namedtuple('Error', 'pos')


def is_identifier(char):
    """
    Test if `char` is a valid Scheme identifier.
    """
    return char.isalnum() or char in builtin_map.keys() or char in ADDITIONAL_BUILTIN_CHARS


class Token:
    """
    A simple Token structure.
    Contains the token type, value,
    and the position of the token.
    """

    def __init__(self, token_type, val, pos):
        # copy the attributes of the Character object
        # to this class instance.
        self.token_type = token_type
        self.val = val
        self.pos = pos

    def __str__(self):
        return "{}({}) at {}".format(self.token_type, self.val, self.pos)


class TokenTypes:
    """
    A Structure for each possible type
    of token.
    """
    BOOLEAN = 'BOOLEAN'
    NUMBER = 'NUMBER'
    IDENTIFIER = 'IDENTIFIER'
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    QUOTE = 'QUOTE'


class Lexer:
    """
    A simple lexer based upon the "maximal munch" rule.
    """

    def __init__(self, buffer):
        """
        Initialize the lexer with buffer as input.
        """
        self.buffer = buffer
        self.pos = 0

    def next_token(self):
        """
        Return the next token(Which is a token object.)
        found in the input buffer. None is returned if we've
        reached the end of the buffer.
        If a lexing error occurs(The current character
        is not known), a LexerError is raised.
        """
        # Continue to skip past garbage characters.
        while self._get_char(self.pos) in GARBAGE_CHARS:
            self._skip_comments()
            self._skip_whitespace()

        if self._get_char(self.pos) is None:
            return None
        char = self.buffer[self.pos]
        if char == '#' and self.buffer[self.pos + 1] in TRUE_OR_FALSE_CHARS:
            return self._process_boolean()
        elif char.isdigit() or char in ADD_OR_SUB_CHARS and self.buffer[self.pos + 1].isdigit():
            return self._process_number()
        elif is_identifier(char):
            return self._process_identifier()
        elif char == '(':
            return self._process_lparen()
        elif char == ')':
            return self._process_rparen()
        elif char == "'":
            return self._process_quote()
        else:
            return Error(self.pos)

    def _skip_whitespace(self):
        """
        Skip past all characters which are whitespace.
        """
        while self._get_char(self.pos):
            if self.buffer[self.pos] in GARBAGE_CHARS:
                self.pos += 1
            else:
                break

    def _skip_comments(self):
        """
        Skip past all characters in the comment.
        """
        if self._get_char(self.pos) != ';':
            return
        while self._get_char(self.pos) and self._get_char(self.pos) != '\n':
            self.pos += 1

    def _process_boolean(self):
        """
        Construct a boolean Token.
        """
        retval = Token(TokenTypes.BOOLEAN, self.buffer[self.pos:self.pos + 2], self.pos)
        self.pos += 2
        return retval

    def _process_number(self):
        """
        Construct a numeric Token.
        """
        endpos = self.pos + 1
        while self._get_char(endpos) and self._get_char(endpos).isdigit():
            endpos += 1
        retval = Token(TokenTypes.NUMBER, self.buffer[self.pos:endpos], self.pos)
        self.pos = endpos
        return retval

    def _process_identifier(self):
        """
        Construct an identifier Token.
        """
        endpos = self.pos + 1
        while self._get_char(endpos) and is_identifier(self._get_char(endpos)):
            endpos += 1
        retval = Token(TokenTypes.IDENTIFIER, self.buffer[self.pos:endpos], self.pos)
        self.pos = endpos
        return retval

    def _process_lparen(self):
        """
        Construct a left parenthesis Token.
        """
        retval = Token(TokenTypes.LPAREN, self.buffer[self.pos], self.pos)
        self.pos += 1
        return retval

    def _process_rparen(self):
        """
        Construct a right parenthesis Token.
        """
        retval = Token(TokenTypes.RPAREN, self.buffer[self.pos], self.pos)
        self.pos += 1
        return retval

    def _process_quote(self):
        """
        Construct a quote Token.
        """
        retval = Token(TokenTypes.QUOTE, self.buffer[self.pos], self.pos)
        self.pos += 1
        return retval

    def _get_char(self, pos):
        """
        Try and get the next character from the buffer.
        If an IndexError is raised, return None.
        """
        try:
            return self.buffer[pos]
        except IndexError:
            return None

