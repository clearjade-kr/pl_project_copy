r"""Chario Class & methods for syntax analyzer.

Deleted EF : SUB - substitute character(ASCII), replaced with None.
Deleted TAB - "\t" - Not using in example code of JAVA.
Deleted println, openFile, saveFile, writeFile methods in JAVA example since not using GUI.
Deleted readFile in JAVA example as this is handled by CUI module.
"""


from typing import List


class Chario(object):
    """Reads source program in text file and provides stream of characters to Scanner.

    Attributes:
        src: List of strings with source program lines as elements.
        line: Current line to be given by get_line() method.
        total_error: Number of errors caught while reading source program.
        column: Current integer to get the character at current line for get_char() method.
        line_number: The index of current line in source file for print out at next_line() method.
    """

    def __init__(self, input_iter) -> None:
        """Construct Chario class with file stream object."""
        self.src: List[str] = list(input_iter)
        self.line: str = ""
        self.total_error: int = 0
        self.column: int = 0
        self.line_number: int = 0

    # def reset(self) -> None:
    #     """Reset the class instance reading process."""
    #     self.line = ""
    #     self.total_error = 0
    #     self.line_number = 0
    #     self.column = 0

    @classmethod
    def make_space(cls, number: int) -> str:
        """Make specific number of spaces to print indentations.

        Args:
            number: Number of spaces needed.

        Returns:
            A string of empty spaces needed.
        """
        s: str = ""
        for _ in range(number):
            s += " "
        return s

    def put_error(self, message: str) -> None:
        """Print error message at the console and counts errors during Compilation.

        Args:
            message: Error message caught during compilation.
        """
        self.total_error += 1
        spaces: str = Chario.make_space(self.column)
        print(spaces + "ERROR > " + message)

    def put_error_alt(self, message: str) -> None:
        """Print error message at the console and counts errors during Compilation.

        Args:
            message: Error message caught during compilation.
        """
        self.total_error += 1
        print("{}ERROR > {}".format((" " * self.column), message))

    def report_errors(self):
        """Print number of errors caught in compilation at console."""
        print("\nCompilation complete")
        if self.total_error == 0:
            print("No errors reported")
        elif self.total_error == 1:
            print("1 error reported")
        else:
            print(self.total_error, "errors reported")

    def get_char(self) -> str:
        if self.column >= len(self.line):
            self.next_line()
        if self.line:
            self.column += 1
            return self.line[self.column - 1]
        return None

    def next_line(self) -> None:
        self.column = 0
        if self.line_number < len(self.src):
            self.line = self.get_line()
            self.line_number += 1
            print("{:>2} > {}".format(self.line_number, self.line))
        else:
            self.line = None

    def get_line(self) -> str:
        if self.src is None or len(self.src) == 0:
            return ""
        else:
            return self.src[self.line_number]
