"""
parser.py
----------------------------------------

Parser for a subset of Scheme. Follows the grammar defined in R5RS
7.1.2 (External Representations).
----------------------------------------

Algerbrex(c1dea2n@gmail.com)

All code in this module is
public domain.

Last modified: February 5 2017
"""

from lexer import Lexer, TokenTypes, Error
from expressions import Pair, Number, Symbol, Boolean, Nil


class ParserError(Exception):
    """
    A parser error.
    """
    pass


class Parser:
    """
    A recursive decent Scheme parser.
    """
    def __init__(self, text):
        self.lexer = Lexer(text)
        self.text = text
        self.token = None

    def parse(self):
        """
        The top-level function of this class.
        """
        self._get_token()
        return self._parse_file()

    def _error(self, msg, pos=None):
        """
        Raise an error point to the line and column
        in the source.
        """
        pos = pos or self.token.pos
        num_newlines = self.text.count('\n', 0, pos)
        line_offset = self.text.rfind('\n', 0, pos)
        if line_offset < 0:
            line_offset = 0
        line_no, col_no = num_newlines + 1, pos - line_offset + 3
        line = self.text.split('\n')[line_no - 1]
        raise ParserError(
            '\nAt line {}:\n\n'.format(line_no) +
            line.replace('\t', '') + '\n' + ' ' * col_no + '^\n\n' + msg
        )

    def _get_token(self):
        """
        Get the next token from the lexer. If the lexer returned an Error
        object, raise an error at the index the Error object holds.
        """
        self.token = self.lexer.next_token()
        if isinstance(self.token, Error):
            self._error('syntax error', self.token.pos)

    def _consume(self, token_type):
        """
        A primitive function for RD parers. It:
        - Checks if the current tokens type is equal to
          `token_type`, and raises an error if not
        - Grabs the next token from the lexer.
        """
        if self.token.token_type == token_type:
            self._get_token()
        else:
            self._error("Expected {}. Found {}".format(token_type, self.token.token_type))

    # ------------------------------------------------------------------------
    # Recursive parsing rules. Follows a subset of the grammar defined in R5RS
    # 7.1.2 (External Representations).
    # ------------------------------------------------------------------------
    def _parse_file(self):
        """
        The top-level function for the recursive "chain".
        Expects a sequence of Scheme expressions.
        """
        datums = []
        while self.token:
            datums.append(self._datum())
        return datums

    def _datum(self):
        """
        Parse a datum.
        """
        if self.token.token_type == TokenTypes.LPAREN:
            return self._list()
        elif self.token.token_type == TokenTypes.QUOTE:
            return self._abbreviation()
        else:
            return self._simple_datum()

    def _list(self):
        """
        Parse a Scheme list. To parse the list we first parse all the datums of the
        list into a regular Python list(`datums`). We then transform the list into nested
        Pair expression, representing the structure of the list. The dot(".") is handled by
        keeping track of where it appeared in the list, and raise an error in case of an invalid
        index.
        """
        self._consume(TokenTypes.LPAREN)
        datums = []
        dot_index = 0
        while True:
            if not self.token:
                self._error("Unmatched parentheses at end of input", self.lexer.pos - 3)
            elif self.token.token_type == TokenTypes.RPAREN:
                break
            elif self.token.val == '.':
                if dot_index > 0:
                    self._error('Invalid position of "." in list')
                dot_index = len(datums)
                self._consume(TokenTypes.IDENTIFIER)
            else:
                datums.append(self._datum())
        self._consume(TokenTypes.RPAREN)

        dotted_end = False
        if dot_index > 0:
            if dot_index == len(datums) - 1:
                dotted_end = True
            else:
                self._error('Invalid position of "." in list')
        cdr = Nil()
        if dotted_end:
            cdr = datums[-1]
            datums = datums[:-1]
        for datum in reversed(datums):
            cdr = Pair(datum, cdr)
        return cdr

    def _abbreviation(self):
        """
        Parse an abbreviation(a.k.a quote).
        """
        self._consume(TokenTypes.QUOTE)
        datum = self._datum()
        return Pair(Symbol('quote'), Pair(datum, None))

    def _simple_datum(self):
        """
        Parse a simple datum.
        """
        if self.token.token_type == TokenTypes.BOOLEAN:
            retval = Boolean(self.token.val == '#t')
        elif self.token.token_type == TokenTypes.NUMBER:
            retval = Number(int(self.token.val))
        elif self.token.token_type == TokenTypes.IDENTIFIER:
            retval = Symbol(self.token.val)
        else:
            self._error("Unexpected token: {}".format(self.token.val))
        self._get_token()
        return retval
