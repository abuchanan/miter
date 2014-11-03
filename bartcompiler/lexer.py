import itertools
import logging
import string


log = logging.getLogger('lexer')


def is_newline(c):
    # TODO cross-platform line seps. Multiple chars on windows! so needs multiple states.
    #      or a look ahead
    return c == '\n'

def is_whitespace(c):
    return c == ' '

def is_word_char(c):
    return c in string.ascii_letters + '+-'

def is_single_quote(c):
    return c == "'"

class InvalidWord_SingleQuote(Exception):
    message = 'Invalid word: single quotes are not allowed'

class UnrecognizedInput(Exception):
    message = 'Unrecognized input'

class InvalidID_Newline(Exception):
    message = 'Invalid ID: newlines are not allowed'

class InvalidID_Empty(Exception):
    message = 'Invalid ID: empty'

class InvalidID_Incomplete(Exception):
    message = 'Invalid ID: incomplete'


class Token(object):

    def __init__(self, type, token=''):
        self.type = type
        self.token = token

    def _key(self):
        return self.type, self.token

    def __eq__(self, other):
        return self._key() == other._key()

    def __repr__(self):
        return 'Token({}, {})'.format(self.type, self.token)


class StateMachine(object):

    def __init__(self):
        self.state = 'start'

    def get_type(self, c):
        if self.state == 'start':

            if is_word_char(c):
                self.state = 'word'
                return 'word'

            elif is_single_quote(c):
                self.state = 'start ID'
                return 'ignore'

            elif is_whitespace(c):
                return 'ignore'

            elif is_newline(c):
                self.state = 'newline'
                return 'newline'

            else:
                raise UnrecognizedInput()

        elif self.state == 'newline':
            if is_whitespace(c):
                return 'indent'
            else:
                self.state = 'start'
                return self.get_type(c)

        elif self.state == 'word':

            if is_word_char(c):
                return 'word'

            elif is_whitespace(c):
                self.state = 'start'
                return 'ignore'

            elif is_newline(c):
                self.state = 'newline'
                return 'newline'

            elif is_single_quote(c):
                raise InvalidWord_SingleQuote()

            else:
                raise UnrecognizedInput()

        elif self.state == 'start ID':

            if is_word_char(c):
                self.state = 'ID'
                return 'ID'

            elif is_whitespace(c):
                return 'ignore'

            elif is_newline(c):
                raise InvalidID_Newline()

            elif is_single_quote(c):
                raise InvalidID_Empty()
                
            else:
                raise UnrecognizedInput()

        elif self.state == 'ID':

            if is_word_char(c) or is_whitespace(c):
                return 'ID'

            elif is_newline(c):
                raise InvalidID_Newline()

            elif is_single_quote(c):
                self.state = 'start'
                return 'ignore'

            else:
                raise UnrecognizedInput()

    def finalize(self):
        if self.state == 'start ID' or self.state == 'ID':
            raise InvalidID_Incomplete()


class Lexer(object):

    def lex(self, chars):
        state = StateMachine()
        grouped = itertools.groupby(chars, state.get_type)

        for group_type, group in grouped:
            if group_type == 'ignore':
                pass

            elif group_type == 'word':
                yield Token('word', ''.join(group))

            elif group_type == 'ID':
                yield Token('ID', ''.join(group).strip())

            elif group_type == 'newline':
                yield Token('newline', '')

            elif group_type == 'indent':
                yield Token('indent', ''.join(group))

            else:
                raise UnrecognizedInput()

        state.finalize()
