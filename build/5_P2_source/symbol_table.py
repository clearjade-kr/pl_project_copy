"""SymbolTable class for static semantic analyzer.

Typical usage example:
    new_st = SymbolTable(new_cio)
    st_instance.enter_scope()
    st_instance.exit_scope()
    se_instance.enter_symbol("column_index", "const")
    se_instance.enter_symbol("x")
    se_instance.find_symbol("j")
"""

from typing import Dict, List
import chario
from symbol_entry import SymbolEntry as SymEnt


class SymbolTable(object):
    """A stack of dictionaries containing identifier information.

    Attributes:
        stack: A list of dictionaries with string keys and SymbolEntry values.
        level: An integer representing current scope level.
        chario: A Chario instance for error submission.
    """

    def __init__(self, cio: chario.Chario) -> None:
        """Init with Chario instance."""
        self.stack: List[Dict[str, SymEnt]] = list()
        self.level: int = -1
        self.chario: chario.Chario = cio

    def enter_scope(self) -> None:
        """Increment level attribute and push new symbol table onto stack.

        Print level number if given verbose option.
        """
        self.stack.append(dict())
        self.level += 1
        if self.chario.is_verbose:
            print("*** Entered level {}".format(self.level))

    def exit_scope(self) -> None:
        """Decrement level attribute and pop last symbol table in stack.

        Print level number and symbol table if given verbose option.
        """
        table: Dict[str, SymEnt] = self.stack.pop()
        if self.chario.is_verbose:
            self.__print_table(table)
            print("*** Exited level {}".format(self.level))
        self.level -= 1

    def __print_table(self, table: Dict[str, SymEnt]) -> None:
        """Convert single symbol table into string.

        Args:
            table: A ditionary with string keys and SymbolEntry values.
        """
        print("*** Symbol table for level {}".format(self.level))
        for s in table.values():
            print(s)

    def enter_symbol(self, key: str, role: str = None) -> SymEnt:
        """Enter new symbol into current symbol table.

        Add error to Chario instance if symbol had been previously declared.

        Args:
            key: A string of identifier name.
            role: A string of identifier role.

        Returns:
            A SymbolEntry instance corresponding to newly added identifier.
        """
        table: Dict[str, SymEnt] = self.stack[-1]
        if key in table:
            self.chario.put_error("Identifier already declared in this block.")
            return None
        else:
            s: SymEnt = SymEnt(key, role) if role else SymEnt(key)
            table[key] = s
            return s

    def find_symbol(self, key: str) -> SymEnt:
        """Find symbol in current symbol table.

        Add error to Chario instance if symbol had been previously not declared.

        Args:
            key: A string of identifier name.

        Returns:
            A SymbolEntry instance corresponding to identifier to be found.
        """
        for i in range(len(self.stack) - 1, -1, -1):
            table: Dict[str, SymEnt] = self.stack[i]
            if key in table:
                return table[key]
        self.chario.put_error("Undeclared identifier")
        return None
