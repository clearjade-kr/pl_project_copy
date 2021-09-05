"""Chario Class & methods for syntax analyzer

Deleted EF : SUB - substitute character(ASCII), replaced with None
Deleted TAB - "\t" - Not using in example code of JAVA
Deleted println, openFile, saveFile, writeFile methods in JAVA example since not using GUI.
"""


class Chario:
    """Reads source program in text file
    and provides stream of characters to Scanner.

    Attributes:
        EL: Line changing
        source_program: Total source program code read by Chario in the text file
        line: Current line to be given by get_line() method.
        total_error: Number of errors caught while reading source program.
        column: Current integer to get the character at current line for get_char() method.
        line_number: The index of current line in source file for print out at next_line() method.
    """

    def __init__(self, stream):
        """Constructor for Chario class with file stream object."""
        self.EL: str = "\n"
        # self.EF: str = chr(26)
        # self.TAB: str = "\t"
        self.source_program: str = ""
        self.line: str = ""
        self.total_error: int = 0
        self.column: int = 0
        self.line_number: int = 0

        self.read_file(stream)
        self.reset()

    def reset(self):
        """Resets the reading process of Chario class."""
        self.total_error = 0
        self.line_number = 0
        self.column = 0
        self.line = ""

    def read_file(self, stream):
        """Reads total text file by stream and puts into source_program.
        Throws FileNotFoundError when the file stream gets error.
        """
        try:
            data = stream.readline()
            while data is not None:
                self.source_program += data + "\n"
                data = stream.readline()
        except FileNotFoundError as e:
            print("Error in file input", e)

    def make_space(self, number: int) -> str:
        """Makes specific number of spaces to print indentations.
        Args:
            number: Number of spaces needed.

        Returns:
            A string of empty spaces needed.
        """
        s: str = ""
        for _ in range(number):
            s += " "
        return s

    def put_error(self, message: str):
        """Prints error message at the console and counts errors during Compilation.
        Args:
            message: Error message caught during compilation.
        """
        self.total_error += 1
        spaces: str = self.make_space(self.column)
        print(spaces + "ERROR > " + message)

    def report_errors(self):
        """Prints number of errors caught in compilation at console.
        """
        print("\nCompilation complete")
        if self.total_error == 0:
            print("No errors reported")
        elif self.total_error == 1:
            print("1 error reported")
        else:
            print(self.total_error, "errors reported")

    def get_char(self) -> str:
        """Method to get characters sequentially for scanner.

        Returns:
            A string of single character.
        """
        ch: str
        if self.column >= len(self.line):
            self.next_line()
        ch = self.line[self.column]
        self.column += 1
        return ch

    def next_line(self):
        """Reads next line of the source_program & counts lines read by get_line() or get_char() methods.
        Prints the current line read by get_line().
        """
        self.column = 0
        self.line = self.get_line()
        if self.line is not None:
            self.line_number += 1
            print(str(self.line_number) + " > " + self.line)

    def get_line(self) -> str:
        """Brings next line of the source_program.
        Pops the first line of source_program and returns that line.

        Returns:
            in_line: The first line of the source_program.
        """
        in_line: str
        first: int
        if self.source_program is None:
            in_line = ""
        else:
            if self.EL in self.source_program:
                first = self.source_program.index(self.EL)
                in_line = self.source_program[:first + 1]
                self.source_program = self.source_program[first + 1:]
            else:
                in_line = self.source_program + self.EL
                self.source_program = ""

        return in_line
