import itertools
import logging
import string


log = logging.getLogger('lexer')


class End(object):

    def __repr__(self):
        return 'End'

def is_newline(c):
    # TODO cross-platform line seps. Multiple chars on windows! so needs multiple states.
    #      or a look ahead
    return c == '\n'

def is_whitespace(c):
    return c == ' '

def is_word_char(c):
    return isinstance(c, str) and c in string.ascii_letters + '+-'

def is_single_quote(c):
    return c == "'"

def is_end(c):
    return isinstance(c, End)

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


class Lexer(object):

    def __init__(self):
        self.reset()

    def reset(self):
        self.state = 'start'
        self.token = ''

    def _add_eof_char(self, chars):
        return itertools.chain(chars, [End()])

    def lex(self, chars):
        chars = self._add_eof_char(chars)

        for c in chars:

            log.debug('-' * 50)
            log.debug('State: ' + self.state)
            log.debug('Current token: ' + self.token)
            log.debug('Current char: ' + repr(c))

            if self.state == 'start':

                if is_word_char(c):
                    self.state = 'word'
                    self.token += c

                elif is_single_quote(c):
                    self.state = 'start ID'

                elif is_whitespace(c) or is_end(c):
                    pass

                elif is_newline(c):
                    yield Token('newline')

                else:
                    raise UnrecognizedInput()

            elif self.state == 'word':

                if is_word_char(c):
                    self.token += c

                elif is_whitespace(c) or is_newline(c) or is_end(c):
                    log.debug('Yield word: ' + self.token)
                    yield Token('word', self.token)

                    if is_newline(c):
                        yield Token('newline')

                    self.reset('newline')

                elif is_single_quote(c):
                    raise InvalidWord_SingleQuote()

                else:
                    raise UnrecognizedInput()

            elif self.state == 'start ID':

                if is_word_char(c):
                    self.state = 'ID'
                    self.token += c

                elif is_whitespace(c):
                    pass

                elif is_newline(c):
                    raise InvalidID_Newline()

                elif is_single_quote(c):
                    raise InvalidID_Empty()

                elif is_end(c):
                    raise InvalidID_Incomplete()

                else:
                    raise UnrecognizedInput()

            elif self.state == 'ID':

                if is_word_char(c) or is_whitespace(c):
                    self.token += c

                elif is_newline(c):
                    raise InvalidID_Newline()

                elif is_end(c):
                    raise InvalidID_Incomplete()

                elif is_single_quote(c):
                    yield Token('ID', self.token.strip())
                    self.reset()

                else:
                    raise UnrecognizedInput()

            elif self.state == 'newline':
                yield Token('newline')
