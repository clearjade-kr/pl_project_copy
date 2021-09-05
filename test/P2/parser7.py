"""Parser with declaration, expression and statements.

Typical usage example:
    new_parser = Parser(cio_instance, scn_instance)
    new_parser.compilation()
"""


from typing import Set
import chario
import scanner
import token
from symbol_entry import SymbolEntry as SymEnt
from symbol_table import SymbolTable as SymTab


ADD_OP_SET: Set[str] = {"plus", "minus"}
MUL_OP_SET: Set[str] = {"mul", "div", "mod"}
REL_OP_SET: Set[str] = {"eq", "ne", "lt", "le", "gt", "ge"}
DEC_OP_SET: Set[str] = {"type", "proc", "id"}
STM_OP_SET: Set[str] = {"loop", "while", "exit", "if", "null", "id", "print"}
L_NAME_SET: Set[str] = {"param", "var"}
R_NAME_SET: Set[str] = {"param", "var", "const"}


def check_number(int_str: str) -> bool:
    """Check if string contains an integer value.

    Args:
        int_str: A string to be checked wether it contains an integer value.

    Returns:
        A bool value indicating if the string contains an integer value.
    """
    if int_str:
        return int_str[1:].isdigit() if int_str[0] == "-" else int_str.isdigit()
    else:
        return False


class Parser(object):
    """Parse and analyze soruce program through recursive descent approach.

    Capable of detecting syntax, lexical or static semantic errors.
    Capable of simple integer arithmetic.

    Attributes:
        chario: A Chario object to read source program and deliver errors.
        scanner: A Scanner object to receive source program tokens.
        token: A Token object to be evaluated.
    """

    def __init__(self, new_cio: chario.Chario, new_scn: scanner.Scanner):
        """Init with Chario and Scanner instances.

        Additionally init symbol table and add default symbols.
        """
        self.chario: chario.Chario = new_cio
        self.scanner: scanner.Scanner = new_scn
        self.token: token.Token = self.scanner.next_token()
        self.table = SymTab(self.chario)
        self.table.enter_scope()
        self.__enter_symbol("type", "boolean")
        self.__enter_symbol("type", "char")
        self.__enter_symbol("type", "integer")
        self.__enter_symbol("const", "true").set_value("true")
        self.__enter_symbol("const", "false").set_value("false")

    def __next_token(self) -> None:
        """Update token attribute with next token from scanner."""
        self.token = self.scanner.next_token()

    def __accept_token(self, expected: str, err_msg: str) -> None:
        """Test if the current token matches the expected token.

        Args:
            expected: A string representing expected token id.
            err_msg: Error message to be printed,
                if the two tokens do not match.
        """
        if self.token.tok_id != expected:
            self.__raise_error(err_msg)
        self.__next_token()

    def __raise_error(self, err_msg: str, with_token: bool = True) -> None:
        """Raise exception with custom error message.

        Args:
            err_msg: Error message to be printed.
        """
        if with_token:
            self.chario.put_error("{} | Token > {}".format(err_msg, self.token))
        else:
            self.chario.put_error(err_msg)
        raise Exception(err_msg)

    def __accept_role(self, sym_ent: SymEnt, expected: Set[str], err_msg: str):
        """Test if the given symbol matches expected role.

        Args:
            expected: A set of string representing expected symbol role(s).
            err_msg: Error message to be printed,
                if the symbol role do not match expected.
        """
        if sym_ent.role and (sym_ent.role not in expected):
            self.chario.put_error(err_msg)

    def __enter_symbol(self, role: str = None, name: str = None) -> SymEnt:
        """Enter new symbol into current symbol table.

        If symbol name is not provided, grab from current token.

        Args:
            key: A string of identifier name.
            role: A string of identifier role.

        Returns:
            A SymbolEntry instance corresponding to newly added identifier.
        """
        sym_ent: SymEnt = None
        if name:
            sym_ent = self.table.enter_symbol(name, role)
        elif self.token.tok_id == "id":
            sym_ent = self.table.enter_symbol(self.token.lit, role)
            self.__next_token()
        else:
            self.__raise_error("Identifier expected")
        return sym_ent

    def __find_symbol(self, name: str = None) -> SymEnt:
        """Find symbol in current symbol table.

        If symbol name is not provided, grab from current token.

        Args:
            key: A string of identifier name.

        Returns:
            A SymbolEntry instance corresponding to identifier to be found.
        """
        sym_ent: SymEnt = None
        if name:
            sym_ent = self.table.find_symbol(name)
        elif self.token.tok_id == "id":
            sym_ent = self.table.find_symbol(self.token.lit)
            self.__next_token()
        else:
            self.__raise_error("Identifier expected")
        return sym_ent

    # Starting from below are methods implementing TinyAda EBNF.
    def compilation(self) -> None:
        """Run compilation."""
        if self.chario.src:
            self.__subprogram_body()
            self.__accept_token("eof", "Unexpected file termination")
            self.table.exit_scope()
            self.chario.report_errors()

    def __subprogram_body(self) -> None:
        self.__subprogram_spec()
        self.__accept_token("is", "'is' expected")
        self.__declarative_part()
        self.__accept_token("begin", "'begin' expected")
        self.__seq_of_statements()
        self.__accept_token("end", "'end' expected")
        self.table.exit_scope()
        if self.token.tok_id == "id":
            self.__accept_role(self.__find_symbol(), {"proc"}, "Procedure name expected")
        self.__accept_token("semi", "';' expected")

    def __declarative_part(self) -> None:
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
            self.__raise_error("Error for [basic_declaration]")

    def __obj_num_declaration(self) -> None:
        sym_ent: SymEnt = self.__identifier_list()
        self.__accept_token("colon", "':' expected")
        if self.token.tok_id == "const":  # numberDeclaration
            sym_ent.set_role("const")
            self.__next_token()
            self.__accept_token("assign", "':=' expected")
            exp_val: str = self.__expression()
            if exp_val:
                sym_ent.set_value(exp_val)
        else:  # objectDeclaration
            sym_ent.set_role("var")
            self.__type_definition()
        self.__accept_token("semi", "';' expected")

    def __identifier_list(self) -> SymEnt:
        sym_ent: SymEnt = self.__enter_symbol()
        while self.token.tok_id == "comma":
            self.__next_token()
            sym_ent.append(self.__enter_symbol())
        return sym_ent

    def __type_declaration(self) -> None:
        self.__accept_token("type", "'type' expected")
        self.__enter_symbol("type")
        self.__accept_token("is", "'is' expected")
        self.__type_definition()
        self.__accept_token("semi", "';' expected")

    def __type_definition(self) -> None:
        if self.token.tok_id == "l_par":
            self.__enum_type_definition()
        elif self.token.tok_id == "array":
            self.__array_type_definition()
        elif self.token.tok_id == "range":
            self.__range()
        elif self.token.tok_id == "id":
            self.__accept_role(self.__find_symbol(), {"type"}, "Type name expected")
        else:
            self.__raise_error("Error for [type_definition]")

    def __range(self) -> None:
        self.__accept_token("range", "'range' expected")
        self.__simple_expression()
        self.__accept_token("to", "'..' expected")
        self.__simple_expression()

    def __index(self) -> None:
        if self.token.tok_id == "range":
            self.__range()
        elif self.token.tok_id == "id":
            self.__accept_role(self.__find_symbol(), {"type"}, "Type name expected")
        else:
            self.__raise_error("Error for [index]")

    def __enum_type_definition(self) -> None:
        self.__accept_token("l_par", "'(' expected")
        self.__identifier_list().set_role("const")
        self.__accept_token("r_par", "')' expected")

    def __array_type_definition(self) -> None:
        self.__accept_token("array", "'array' expected")
        self.__accept_token("l_par", "'(' expected")
        self.__index()
        while self.token.tok_id == "comma":
            self.__next_token()
            self.__index()
        self.__accept_token("r_par", "')' expected")
        self.__accept_token("of", "'of' expected")
        self.__accept_role(self.__find_symbol(), {"type"}, "Type name expected")

    def __subprogram_spec(self) -> None:
        self.__accept_token("proc", "'procedure' expected")
        self.__enter_symbol("proc")
        self.table.enter_scope()
        if self.token.tok_id == "l_par":
            self.__formal_part()

    def __formal_part(self) -> None:
        self.__accept_token("l_par", "'(' expected")
        self.__parameter_specification()
        while self.token.tok_id == "semi":
            self.__next_token()
            self.__parameter_specification()
        self.__accept_token("r_par", "')' expected")

    def __parameter_specification(self) -> None:
        self.__identifier_list().set_role("param")
        self.__accept_token("colon", "':' expected")
        self.__mode()
        self.__accept_role(self.__find_symbol(), {"type"}, "Type name expected")

    def __mode(self) -> None:
        if self.token.tok_id == "in":
            self.__next_token()
        if self.token.tok_id == "out":
            self.__next_token()

    def __condition(self) -> None:
        self.__expression()

    def __expression(self) -> str:
        val: str = self.__relation()
        no_logic_op: bool = True
        if self.token.tok_id == "and":
            no_logic_op = False
            while self.token.tok_id == "and":
                self.__next_token()
                self.__relation()
        elif self.token.tok_id == "or":
            no_logic_op = False
            while self.token.tok_id == "or":
                self.__next_token()
                self.__relation()
        return val if (check_number(val) and no_logic_op) else None

    def __relation(self) -> str:
        val: str = self.__simple_expression()
        no_rel_op: bool = True
        if self.token.tok_id in REL_OP_SET:
            no_rel_op = False
            self.__next_token()
            self.__simple_expression()
        return val if (check_number(val) and no_rel_op) else None

    def __simple_expression(self) -> str:
        cur_add_op: str = None
        if self.token.tok_id in ADD_OP_SET:
            cur_add_op = self.token.tok_id
            self.__next_token()
        val1: str = self.__term()
        if cur_add_op and check_number(val1):
            if cur_add_op == "minus":
                val1 = str(0 - int(val1))
        while self.token.tok_id in ADD_OP_SET:
            cur_add_op = self.token.tok_id
            self.__next_token()
            val2: str = self.__term()
            if check_number(val1) and check_number(val2):
                if cur_add_op == "plus":
                    val1 = str(int(val1) + int(val2))
                else:
                    val1 = str(int(val1) - int(val2))
        return val1 if check_number(val1) else None

    def __term(self) -> str:
        val1: str = self.__factor()
        while self.token.tok_id in MUL_OP_SET:
            cur_mul_op: str = self.token.tok_id
            self.__next_token()
            val2: str = self.__factor()
            if check_number(val1) and check_number(val2):
                if cur_mul_op == "mul":
                    val1 = str(int(val1) * int(val2))
                elif cur_mul_op == "div":
                    val1 = str(int(val1) // int(val2))
                else:
                    val1 = str(int(val1) % int(val2))
        return val1 if check_number(val1) else None

    def __factor(self) -> str:
        if self.token.tok_id == "not":
            self.__next_token()
            self.__primary()
            return None
        else:
            val1: str = self.__primary()
            if self.token.tok_id == "exp":
                self.__next_token()
                val2: str = self.__primary()
                if check_number(val1) and check_number(val2):
                    val1 = str(int(val1) ** int(val2))
            return val1 if check_number(val1) else None

    def __primary(self) -> str:
        val: str = None
        if self.token.tok_id == "int":
            val = self.token.lit
            self.__next_token()
        elif self.token.tok_id == "l_par":
            self.__next_token()
            val = self.__expression()
            self.__accept_token("r_par", "')' expected")
        elif self.token.tok_id == "id":
            sym_ent: SymEnt = self.__name()
            self.__accept_role(sym_ent, R_NAME_SET, "Variable, parameter or constant name expected")
            val = sym_ent.val
        else:
            self.__raise_error("Error for [primary]")
        return val

    def __name(self) -> SymEnt:
        sym_ent: SymEnt = self.__find_symbol()
        if self.token.tok_id == "l_par":
            self.__indexed_component()
        return sym_ent

    def __indexed_component(self) -> None:
        self.__accept_token("l_par", "'(' expected")
        self.__expression()
        while self.token.tok_id == "comma":
            self.__next_token()
            self.__expression()
        self.__accept_token("r_par", "')' expected")

    def __seq_of_statements(self) -> None:
        self.__statement()
        while self.token.tok_id in STM_OP_SET:
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
        elif self.token.tok_id in ("while", "loop"):
            self.__loop_statement()
        elif self.token.tok_id == "print":
            self.__print_statement()
        else:
            self.__raise_error("Error for [statement]")

    def __null_statement(self) -> None:
        self.__accept_token("null", "'null' expected")
        self.__accept_token("semi", "';' expected")

    def __loop_statement(self) -> None:
        if self.token.tok_id == "while":
            self.__accept_token("while", "'while' expected")
            self.__condition()
        self.__accept_token("loop", "'loop' expected")
        self.__seq_of_statements()
        self.__accept_token("end", "'end' expected")
        self.__accept_token("loop", "'loop' expected")
        self.__accept_token("semi", "';' expected")

    def __if_statement(self) -> None:
        self.__accept_token("if", "'if' expected")
        self.__condition()
        self.__accept_token("then", "'then' expected")
        self.__seq_of_statements()
        while self.token.tok_id == "elsif":
            self.__accept_token("elsif", "'elsif' expected")
            self.__condition()
            self.__accept_token("then", "'then' expected")
            self.__seq_of_statements()
        if self.token.tok_id == "else":
            self.__accept_token("else", "'else' expected")
            self.__seq_of_statements()
        self.__accept_token("end", "'end' expected")
        self.__accept_token("if", "'if' expected")
        self.__accept_token("semi", "';' expected")

    def __exit_statement(self) -> None:
        self.__accept_token("exit", "'exit' expected")
        if self.token.tok_id == "when":
            self.__accept_token("when", "'when' expected")
            self.__condition()
        self.__accept_token("semi", "';' expected")

    def __assign_call_statement(self) -> None:
        sym_ent: SymEnt = self.__name()
        if self.token.tok_id == "assign":
            self.__accept_role(sym_ent, L_NAME_SET, "Variable or parameter name expected")
            self.__next_token()
            exp_val: str = self.__expression()
            if exp_val:
                sym_ent.set_value(exp_val)
        elif self.token.tok_id == "l_par":
            self.__accept_role(sym_ent, {"proc"}, "Procedure name expected")
            self.__indexed_component()
        self.__accept_token("semi", "';' expected")

    def __print_statement(self) -> None:
        self.__accept_token("print", "'print' expected")
        self.__accept_token("l_par", "'(' expected")
        exp_val: str = self.__expression()
        if exp_val:
            print(exp_val)
        else:
            self.__raise_error("Illegal [print] operand", False)
        self.__accept_token("r_par", "')' expected")
        self.__accept_token("semi", "';' expected")
