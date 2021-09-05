"""Scanner class for syntax analyzer.

Typical usage example:
    new_scn = Scanner(cio_instance)
    new_tok = scan_instance.next_token()
"""


from typing import List
import token
import chario


class Scanner(object):
    """Recognizes token from chario text stream and provide token to parser.

    Attributes:
        chario: A chario object to receive text stream from.
        buffer: A list of strings for temporary character storage.
        char: A string of single character received from chario.
    """

    def __init__(self, cio: chario.Chario) -> None:
        """Init with chario."""
        self.chario: chario.Chario = cio
        self.buffer: List[str] = list()
        self.char: str = self.chario.get_char()

    def __get_char(self) -> None:
        """Update self char attribute with next character from chario."""
        self.char = self.chario.get_char()

    def __buffer_to_str(self) -> str:
        """Create string by joining characters in buffer attribute.

        Return:
            A string combined from characters in buffer.
        """
        return "".join(self.buffer) if self.buffer else None

    def __reset_buffer(self) -> None:
        """Clear buffer attribute."""
        self.buffer.clear()

    def __skip_whitespaces(self) -> None:
        """Read stream until character is not whitespace."""
        while self.char.isspace() and self.chario:
            self.__get_char()

    def __get_token_integer(self) -> token.Token:
        """Read stream and recognize for integer token."""
        while self.char.isdigit():
            self.buffer.append(self.char)
            self.__get_char()
        return token.Token(self.__buffer_to_str(), "int")

    def __get_token_keyword_identifier(self) -> token.Token:
        """Read stream and recognize for identifier or keyword token."""
        while self.char.isalpha() or self.char.isdigit() or self.char == "_":
            self.buffer.append(self.char)
            self.__get_char()
        word: str = self.__buffer_to_str()
        new_tok: token.Token = token.lit_to_tok(word)
        return new_tok if new_tok else token.Token(word, "id")

    def __get_token_double_operator(self) -> token.Token:
        """Read stream and recognize for double operator token."""
        self.buffer.append(self.char)
        self.__get_char()
        self.buffer.append(self.char)
        new_tok: token.Token = token.lit_to_tok(self.__buffer_to_str())
        return new_tok

    def __get_token_single_operator(self) -> token.Token:
        """Read stream and recognize for single operator token."""
        return token.lit_to_tok(self.buffer[0])

    def next_token(self) -> token.Token:
        """Recognize token from text stream provided by chario object.

        Return:
            A Token class instance containinig recognized token.
        """
        self.__skip_whitespaces()
        if self.char == chr(3):
            return token.Token("eof", "eof")
        self.__reset_buffer()
        new_tok: token.Token = None
        if self.char.isdigit():
            new_tok = self.__get_token_integer()
        elif self.char.isalpha():  # Ada lang allows only letter start
            new_tok = self.__get_token_keyword_identifier()
        else:
            new_tok = self.__get_token_double_operator()
            if not new_tok:
                new_tok = self.__get_token_single_operator()
                if not new_tok:
                    self.chario.put_error("An unknown symbol")
            else:
                self.__get_char()
        return new_tok if new_tok else self.next_token()
