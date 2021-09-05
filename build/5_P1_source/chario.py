"""Chario class for syntax analyzer.

Typical usage example:
    new_cio = Chario("C:/pl_project/test.txt", False)
    cio_instance.put_error("';' expected")
    cio_instance.report_errors()
    new_char = cio_instance.get_char()
"""


from typing import List
import os.path


class Chario(object):
    """Read raw source program and provide text stream for scanner.

    Attributes:
        src: A list of strings with source program lines as elements.
        line: A string of current source program line.
        err_count: An int of error count caught while parsing.
        column: An int of index of current character in source program line.
        line_number: An int of index for current line in source program.
    """

    def __init__(self, in_file: str, is_verbose: bool) -> None:
        """Init with input source program filepath and verbose option."""
        self.src: List[str] = None
        if os.path.isfile(in_file):
            in_file_obj = open(in_file)
            self.src = in_file_obj.readlines()
            in_file_obj.close()
        else:
            print("E: Invalid filepath or faulty file: {}".format(in_file))
        self.is_verbose: bool = is_verbose
        self.line: str = ""
        self.err_count: int = 0
        self.column: int = 0
        self.line_count: int = 0

    def __print_line(self) -> None:
        print("#{:>2}: {}".format(self.line_count, self.line.rstrip()))

    def put_error(self, message: str) -> None:
        """Increment error count and optionally print error message.

        Args:
            message: A string of error message caught during compilation.
        """
        self.err_count += 1
        if not self.is_verbose and self.line:
            self.__print_line()
        print("{}E: {}".format((" " * (3 + self.column)), message))

    def report_errors(self):
        """Print number of errors caught during compilation."""
        if self.is_verbose:
            print("\nCompilation complete")
        if self.err_count == 0:
            if self.is_verbose:
                print("No errors reported")
        elif self.err_count == 1:
            print("1 error reported")
        else:
            print(self.err_count, " errors reported")

    def get_char(self) -> str:
        """Get next character from current source program line.

        Returns:
            A string of current source program character.
        """
        if self.column >= len(self.line):
            self.next_line()
        if self.line is None:
            return chr(3)
        self.column += 1
        return self.line[self.column - 1].lower()

    def next_line(self) -> None:
        """Update line attribute to next line in the source program."""
        self.column = 0
        if self.src and self.line_count < len(self.src):
            self.line = self.src[self.line_count]
            self.line_count += 1
            if self.is_verbose:
                self.__print_line()
        else:
            self.line = None
