"""SymbolEntry class for static semantic analyzer.

Typical usage example:
    new_se = SymbolEntry("column_index")
    new_se = SymbolEntry("column_index", "const")
    new_se = SymbolEntry("i", "var", "1")
    se_instance.append(new_se)
    se_instance.set_role("param")
    se_instance.set_value("1")
"""

from typing import Set


class SymbolEntry(object):
    """Record information about identifier.

    Attributes:
        valid_roles: A set of strings containing valid roles.
        name: A string of name.
        role: A string of role.
        val: A string of value.
        next: A SymbolEntry instance appended.
    """

    # A set of strings containg valid symbol entry roles
    valid_roles: Set[str] = {"const", "var", "type", "proc", "param"}

    def __init__(self, id: str, role: str = None, val: str = None) -> None:
        """Init with identifier name, optional role, and optional value."""
        self.name: str = id
        self.role: str = role if (role and role in self.valid_roles) else None
        self.val: str = val if val else None
        self.next: SymbolEntry = None

    def __str__(self) -> str:
        """Convert contents into string.

        Returns:
            A string representing self contents.
        """
        if self.role == "const":
            role = "Constant"
        elif self.role == "var":
            role = "Variable"
        elif self.role == "type":
            role = "Type"
        elif self.role == "proc":
            role = "Procedure"
        elif self.role == "param":
            role = "Parameter"
        else:
            role = "None"
        return "Name:{:<16} | Role:{:<5} | Value: {}".format(self.name, role, self.val)

    def append(self, se) -> None:
        """Append SymbolEntry instance.

        Args:
            se: A SymbolEntry instance to be appended to self.
        """
        if not self.next:
            self.next = se
        else:
            self.next.append(se)

    def set_role(self, role: str) -> None:
        """Set a role.

        Args:
            role: A string of identifier role.
        """
        self.role = role if (role and role in self.valid_roles) else None
        if self.next:
            self.next.set_role(role)

    def set_value(self, val: str) -> None:
        """Set a value.

        Args:
            val: A string of identifier value.
        """
        self.val = val if val else None
        if self.next:
            self.next.set_value(val)
