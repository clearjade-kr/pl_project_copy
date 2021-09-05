"""Token class and functions for syntax analyzer.

Typical usage example:
    new_tok = Token(":=")
    new_tok = Token("100", "int")
    new_tok = Token("i", "id")
    new_tok = Token("eof", "eof")
    tok_str = str(Token("+"))
    new_tok = lit_to_tok(";")
"""


from typing import Dict, Set


# TOKEN_ID_DICT converts literal code to token id.
TOK_ID_DICT: Dict[str, str] = dict()
TOK_ID_DICT["is"] = "is"
TOK_ID_DICT["begin"] = "begin"
TOK_ID_DICT["end"] = "end"
TOK_ID_DICT["semi"] = ";"
TOK_ID_DICT["colon"] = ":"
TOK_ID_DICT["const"] = "constant"
TOK_ID_DICT["assign"] = ":="
TOK_ID_DICT["comma"] = ","
TOK_ID_DICT["type"] = "type"
TOK_ID_DICT["range"] = "range"
TOK_ID_DICT["to"] = ".."
TOK_ID_DICT["l_par"] = "("
TOK_ID_DICT["r_par"] = ")"
TOK_ID_DICT["array"] = "array"
TOK_ID_DICT["of"] = "of"
TOK_ID_DICT["proc"] = "procedure"
TOK_ID_DICT["in"] = "in"
TOK_ID_DICT["out"] = "out"
TOK_ID_DICT["null"] = "null"
TOK_ID_DICT["if"] = "if"
TOK_ID_DICT["then"] = "then"
TOK_ID_DICT["elsif"] = "elsif"
TOK_ID_DICT["else"] = "else"
TOK_ID_DICT["loop"] = "loop"
TOK_ID_DICT["while"] = "while"
TOK_ID_DICT["exit"] = "exit"
TOK_ID_DICT["when"] = "when"
TOK_ID_DICT["and"] = "and"
TOK_ID_DICT["or"] = "or"
TOK_ID_DICT["exp"] = "**"
TOK_ID_DICT["not"] = "not"
TOK_ID_DICT["eq"] = "="
TOK_ID_DICT["ne"] = "/="
TOK_ID_DICT["lt"] = "<"
TOK_ID_DICT["le"] = "<="
TOK_ID_DICT["gt"] = ">"
TOK_ID_DICT["ge"] = ">="
TOK_ID_DICT["plus"] = "+"
TOK_ID_DICT["minus"] = "-"
TOK_ID_DICT["mul"] = "*"
TOK_ID_DICT["div"] = "/"
TOK_ID_DICT["mod"] = "mod"

# LIT_DICT converts token id to literal code.
LIT_DICT: Dict[str, str] = dict()
for tok_id, lit in TOK_ID_DICT.items():
    LIT_DICT[lit] = tok_id


class Token(object):
    """Mediates transfer of token / literal code information.

    Attributes:
        valid_tok_type: A set of strings containing valid token types.
        lit: A string of literal code.
        tok_id: A string of token id.
    """

    valid_tok_type: Set[str] = {"int", "id", "type", "eol", "eof"}

    def __init__(self, lit: str, tok_type: str = None) -> None:
        """Init with literal code and optional token type."""
        self.lit: str = lit
        self.tok_id: str = tok_id
        if tok_type and tok_type in self.valid_tok_type:
            self.tok_id: str = tok_type
        else:
            self.tok_id: str = LIT_DICT[lit] if lit in LIT_DICT else None

    def __str__(self) -> str:
        """Convert contents into string."""
        return "{}: {}".format(self.tok_id, self.lit)


def lit_to_tok(lit: str) -> Token:
    """Convert literal code into Token instance.

    Returns None if given literal code is not identified.

    Args:
        lit: A string of literal code.

    Returns:
        A Token instance for given literal code.
    """
    return Token(lit) if lit in LIT_DICT else None
