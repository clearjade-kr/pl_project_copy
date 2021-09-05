"""Parser with declaration, expression and statements."""


from typing import Set
import chario
import scanner
import token


ADD_OP_SET: Set[str] = {"plus", "minus"}
MUL_OP_SET: Set[str] = {"mul", "div", "mod"}
REL_OP_SET: Set[str] = {"eq", "ne", "lt", "le", "gt", "ge"}
DEC_OP_SET: Set[str] = {"type", "proc", "id"}
STATEMENT_OP_SET: Set[str] = {"loop", "while", "exit", "if", "null", "id"}


class Parser(object):
    """Receives token from scanner and analyzes the syntax of program through top-down parsing

    Attributes:
        chario: chario object to raise the error
        scanner: scanner object to receive token
        token: token object received from scanner
    """
    def __init__(self, new_cio: chario.Chario, new_scn: scanner.Scanner):
        """Init with chario and scanner"""
        self.chario: chario.Chario = new_cio
        self.scanner: scanner.Scanner = new_scn
        self.token: token.Token = self.scanner.next_token()

    # def reset(self) -> None:
    #   self.scanner.reset()
    #   self.next_token()

    def next_token(self) -> None:
        """Get token from scanner"""
        self.token = self.scanner.next_token()

    def test_token(self, expected: str, err_msg: str) -> None:
        """Test if the current token matches the expected token

        Args:
            expected: Expected token id
            err_msg: Error message to be raised when the current token and the expected token do not match
        """
        if self.token.tok_id != expected:
            self.raise_error(err_msg)
        self.next_token()

    def raise_error(self, err_msg: str) -> None:
        """Raise error

        Args:
            err_msg: Error message to be raised
        """
        self.chario.put_error(err_msg)
        raise Exception(err_msg)

    def compilation(self) -> None:
        """Start compilation"""
        self.__subprogram_body()

    def __subprogram_body(self) -> None:
        self.__subprogram_spec()
        self.test_token("is", "'is' expected")
        self.__declarative_part()
        self.test_token("begin", "'begin' expected")
        self.__seq_of_statements()
        self.test_token("end", "'end' expected")
        if self.token.tok_id == "id":
            self.next_token()
        self.test_token("semi", "';' expected")

    def __declarativePart(self) -> None:
        while self.token.tok_id in DEC_OP_SET:
            self.__basic_declaration()

    def __basic_declaration(self) -> None:
        if self.token.tok_id == "type":
            self.__type_declaration()
        elif self.token.tok_id == "proc":
            self.__subprogram_body()
        elif self.token.tok_id == "id":
            self.__obj_num_declaration()
        else:
            self.raise_error("error for [basic_declaration]")

    def __obj_num_declaration(self) -> None:
        self.__identifier_list()
        self.test_token("colon", "':' expected")
        if self.token.tok_id == "const":  # numberDeclaration
            self.next_token()
            self.test_token("assign", "':=' expected")
            self.__expression()
        else:  # objectDeclaration
            self.__type_definition()
        self.test_token("semi", "';' expected")

    def __identifier_list(self) -> None:
        self.test_token("id", "identifier expected")
        while self.token.tok_id == "comma":
            self.next_token()
            self.test_token("id", "identifier expected")

    def __type_declaration(self) -> None:
        self.test_token("type", "'type' expected")
        self.test_token("id", "identifier expected")
        self.test_token("is", "'is' expected")
        self.__type_definition()
        self.test_token("semi", "';' expected")

    def __type_definition(self) -> None:
        if self.token.tok_id == "l_par":
            self.__enum_type_definition()
        elif self.token.tok_id == "array":
            self.__array_type_definition()
        elif self.token.tok_id == "range":
            self.__range()
        elif self.token.tok_id == "id":
            self.__name()
        else:
            self.raise_error("error for [type_definition]")

    def __range(self) -> None:
        self.test_token("range", "'range' expected")
        self.__simple_expression()
        self.test_token("to", "'..' expected")
        self.__simple_expression()

    def __index(self) -> None:
        if self.token.tok_id == "range":
            self.__range()
        elif self.token.tok_id == "id":
            self.__name()
        else:
            self.raise_error("error for [index]")

    def __enum_type_definition(self) -> None:
        self.test_token("l_par", "'(' expected")
        self.__identifier_list()
        self.test_token("r_par", "')' expected")

    def __array_type_definition(self) -> None:
        self.test_token("array", "'array' expected")
        self.test_token("l_par", "'(' expected")
        self.__index()
        while self.token.tok_id == "comma":
            self.token = self.scanner.next_token()
            self.__index()
        self.test_token("r_par", "')' expected")
        self.test_token("of", "'of' expected")
        self.__name()

    def __subprogram_spec(self) -> None:
        self.test_token("proc", "'procedure' expected")
        self.test_token("id", "identifier expected")
        if self.token.tok_id == "l_par":
            self.__formal_part()

    def __formal_part(self) -> None:
        self.test_token("l_par", "'(' expected")
        self.__parameter_specification()
        while self.token.tok_id == "semi":
            self.next_token()
            self.__parameter_specification()
        self.test_token("r_par", "')' expected")

    def __parameter_specification(self) -> None:
        self.__identifier_list()
        self.test_token("colon", "':' expected")
        self.__mode()
        self.__name()

    def __mode(self) -> None:
        if self.token.tok_id == "in":
            self.next_token()
            if self.token.tok_id == "out":
                self.next_token()
        elif self.token.tok_id == "out":
            self.next_token()

    def __condition(self) -> None:
        self.__expression()

    def __expression(self) -> None:
        self.__relation()
        if self.token.tok_id == "and":
            while self.token.tok_id == "and":
                self.next_token()
                self.__relation()
        elif self.token.tok_id == "or":
            while self.token.tok_id == "or":
                self.next_token()
                self.__relation()

    def __relation(self) -> None:
        self.__simple_expression()
        if self.token.tok_id in REL_OP_SET:
            self.next_token()
            self.__simple_expression()

    def __simple_expression(self) -> None:
        if self.token.tok_id in ADD_OP_SET:
            self.next_token()
        self.__term()
        while self.token.tok_id in ADD_OP_SET:
            self.next_token()
            self.__term()

    def __term(self) -> None:
        self.__factor()
        while self.token.tok_id in MUL_OP_SET:
            self.next_token()
            self.__factor()

    def __factor(self) -> None:  # TODO: Validate raising error
        if self.token.tok_id == "not":
            self.next_token()
            self.__primary()
        else:
            self.__primary()
            if self.token.tok_id == "exp":
                self.next_token()
                self.__primary()

    def __primary(self) -> None:
        if self.token.tok_id == "int" or self.token.tok_id == "str":
            self.next_token()
        elif self.token.tok_id == "l_par":
            self.next_token()
            self.__expression()
            self.test_token("r_par", "')' expected")
        elif self.token.tok_id == "id":
            self.__name()
        else:
            self.raise_error("error for [primary]")

    def __name(self) -> None:
        self.test_token("id", "identifer expected")
        if self.token.tok_id == "l_par":
            self.__indexed_component()

    def __indexed_component(self) -> None:
        self.test_token("l_par", "'(' expected")
        self.__expression()
        while self.token.tok_id == "comma":
            self.next_token()
            self.__expression()
        self.test_token("r_par", "')' expected")

    def __seq_of_statements(self) -> None:
        self.__statement()
        while self.token.tok_id in STATEMENT_OP_SET:
            self.__statement()

    def __statement(self) -> None:
        if self.token.tok_id == "id":
            self.__assign_call_statement()
        elif self.token.tok_id == "exit":
            self.__exit_statement()
        elif self.token.tok_id == "if":
            self.__if_statement()
        elif self.token.tok_id == "null":
            self.__null_statement()
        # elif self.token.tok_id in ["while", "loop"]:
        # Tuple is often more cost effecctive than lists for static operations
        elif self.token.tok_id in ("while", "loop"):
            self.__loop_statement()
        else:
            # self.raise_error("Error in statement")
            self.raise_error("error for [statement]")

    def __null_statement(self) -> None:
        self.test_token("null", "'null' expected")
        self.test_token("semi", "';' expected")

    def __loop_statement(self) -> None:
        if self.token.tok_id == "while":
            self.test_token("while", "'while' expected")
            self.__condition()
        self.test_token("loop", "'loop' expected")
        self.__seq_of_statements()
        self.test_token("end", "'end' expected")
        self.test_token("loop", "'loop' expected")
        self.test_token("semi", "';' expected")

    def __if_statement(self) -> None:
        self.test_token("if", "'if' expected")
        self.__condition()
        self.test_token("then", "'then' expected")
        while self.token.tok_id == "elsif":
            self.test_token("elsif", "'elsif' expected")
            self.__condition()
            self.test_token("then", "'then' expected")
            self.__seq_of_statements()
        if self.token.tok_id == "else":
            self.test_token("else", "'else' expected")
            self.__seq_of_statements()
        self.test_token("end", "'end' expected")
        self.test_token("if", "'if' expected")
        self.test_token("semi", "';' expected")

    def __exit_statement(self) -> None:
        self.test_token("exit", "'exit' expected")
        if self.token.tok_id == "when":
            self.test_token("when", "'when' expected")
            self.__condition()
        self.test_token("semi", "';' expected")

    def __assign_call_statement(self) -> None:
        self.__name()
        # if self.token.tok_id == ":=":
        if self.token.tok_id == "assign":
            self.next_token()
            self.__expression()
        self.test_token("semi", "';' expected")
