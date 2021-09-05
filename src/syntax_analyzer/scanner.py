#!/usr/bin/env python
# coding: utf-8

"""Scanner class and functions for syntax analyzer."""

# from typing import Dict, List
from typing import List
import token
import chario

# KEYWORDS_DICT: Dict[str, token.Token] = dict()
# KEYWORDS_DICT["is"] = token.Token("is")
# KEYWORDS_DICT["begin"] = token.Token("begin")
# KEYWORDS_DICT["end"] = token.Token("end")
# KEYWORDS_DICT["type"] = token.Token("type")
# KEYWORDS_DICT["range"] = token.Token("range")
# KEYWORDS_DICT["array"] = token.Token("array")
# KEYWORDS_DICT["procedure"] = token.Token("procedure")
# KEYWORDS_DICT["in"] = token.Token("in")
# KEYWORDS_DICT["out"] = token.Token("out")
# KEYWORDS_DICT["null"] = token.Token("null")
# KEYWORDS_DICT["if"] = token.Token("if")
# KEYWORDS_DICT["elsif"] = token.Token("elsif")
# KEYWORDS_DICT["else"] = token.Token("else")
# KEYWORDS_DICT["loop"] = token.Token("loop")
# KEYWORDS_DICT["while"] = token.Token("while")
# KEYWORDS_DICT["exit"] = token.Token("exit")
# KEYWORDS_DICT["and"] = token.Token("and")
# KEYWORDS_DICT["or"] = token.Token("or")
# KEYWORDS_DICT["not"] = token.Token("not")
# KEYWORDS_DICT["mod"] = token.Token("mod")
# KEYWORDS_DICT["constant"] = token.Token("constant")
# KEYWORDS_DICT["of"] = token.Token("of")
# KEYWORDS_DICT["then"] = token.Token("then")
# KEYWORDS_DICT["when"] = token.Token("when")
#
# SINGLE_OPS_DICT: Dict[str, token.Token] = dict()
# SINGLE_OPS_DICT[";"] = token.Token(";")
# SINGLE_OPS_DICT[":"] = token.Token(":")
# SINGLE_OPS_DICT["="] = token.Token("=")
# SINGLE_OPS_DICT[","] = token.Token(",")
# SINGLE_OPS_DICT["("] = token.Token("(")
# SINGLE_OPS_DICT[")"] = token.Token(")")
# SINGLE_OPS_DICT["<"] = token.Token("<")
# SINGLE_OPS_DICT[">"] = token.Token(">")
# SINGLE_OPS_DICT["+"] = token.Token("+")
# SINGLE_OPS_DICT["-"] = token.Token("-")
# SINGLE_OPS_DICT["*"] = token.Token("*")
# SINGLE_OPS_DICT["/"] = token.Token("/")
#
# DOUBLE_OPS_DICT: Dict[str, token.Token] = dict()
# DOUBLE_OPS_DICT[":="] = token.Token(":=")
# DOUBLE_OPS_DICT[".."] = token.Token("..")
# DOUBLE_OPS_DICT["**"] = token.Token("**")
# DOUBLE_OPS_DICT["/="] = token.Token("/=")
# DOUBLE_OPS_DICT["<="] = token.Token("<=")
# DOUBLE_OPS_DICT[">="] = token.Token(">=")


class Scanner(object):
    """Recognizes token by receiving character from chario and returns token sequence

    Attributes:
        chario: chario object to receive character
        buffer: a list that temporarily stores characters
        char: character received from chario
    """
    def __init__(self, cio: chario.Chario) -> None:
        """Init with chario"""
        self.chario: chario.Chario = cio
        self.buffer: List[str] = list()
        self.char: str = self.chario.get_char()

    def get_char(self) -> None:
        """Get character from chario"""
        self.char = self.chario.get_char()

    def buffer_to_str(self) -> str:
        """Create string by joining characters in buffer

        Return:
            String combined from characters in buffer
        """
        return "".join(self.buffer) if self.buffer else None

    def reset_buffer(self) -> None:
        """Clear buffer"""
        # self.buffer = []
        self.buffer.clear()

    def skip_whitespaces(self) -> None:
        """Receive character until char is not whitespace characters"""
        # while self.char == ' ' or self.char == '\n' or self.char == '\t':
        while self.char.isspace():
            self.get_char()

    def __get_token_integer(self) -> token.Token:
        while self.char.isdigit():
            self.buffer.append(self.char)
            self.get_char()
        # integer = "".join(self.buffer)
        # token = token.Token(integer, "int")
        # return token
        return token.Token(self.buffer_to_str(), "int")

    def __get_token_keyword_identifier(self) -> token.Token:
        # Python Identifier
        while self.char.isalpha() or self.char.isdigit() or self.char == "_":
            self.buffer.append(self.char)
            self.get_char()
        word: str = self.buffer_to_str()
        # token = search_token(KEYWORDS_DICT, word)
        new_tok: token.Token = token.lit_to_tok(word)
        # if is_error_token(token):
        #     token = token.Token(word, "id")
        # return token
        return new_tok if new_tok else token.Token(word, "id")

    def __get_token_double_operator(self) -> token.Token:
        self.buffer.append(self.char)
        self.get_char()
        self.buffer.append(self.char)
        # doubleOp = "".join(self.buffer)
        # token = search_token(DOUBLE_OPS_DICT, doubleOp)
        new_tok: token.Token = token.lit_to_tok(self.buffer_to_str())
        # return token
        return new_tok

    def __get_token_single_operator(self) -> token.Token:
        # token = search_token(SINGLE_OPS_DICT, self.buffer[0])
        # return token
        return token.lit_to_tok(self.buffer[0])

    def next_token(self) -> token.Token:
        """Recognize token by receiving character from chario

        Return:
            Token object
        """
        self.skip_whitespaces()
        self.reset_buffer()
        new_tok: token.Token = None
        if self.char.isdigit():
            new_tok = self.__get_token_integer()
        # elif self.char.isalpha() or self.char == "_":
        elif self.char.isalpha():  # Ada lang allows only letter start
            new_tok = self.__get_token_keyword_identifier()
        else:
            new_tok = self.__get_token_double_operator()
            # if is_error_token(token):
            if not new_tok:
                # token = self.__get_token_single_operator()
                new_tok = self.__get_token_single_operator()
                # if is_error_token(token):
                if not new_tok:
                    self.chario.put_error("An unknown symbol")
                # else:
                #     None
            else:
                # self.char = self.chario.get_char()
                self.get_char()
        # if is_error_token(token):
        #     return self.next_token()
        # else:
        #     return token
        return new_tok if new_tok else self.next_token()


# def is_error_token(token: token.Token) -> bool:
#     if token.new_tok == "err":
#         return True
#     else:
#         return False


# def search_token(tokenDict: Dict, t: str) -> token.Token:
#     try:
#         return tokenDict[t]
#     except Exception:
#         return token.Token("error", "err")
