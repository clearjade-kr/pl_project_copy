"""Command line user interface for syntax and static semantic analyzer."""


import argparse
import sys
import chario
import scanner
import parser7


class Logger(object):
    """Mediates streaming output to console and log file.

    Attributes:
        terminal: Console stdout.
        out_file: A file object to write output.
    """

    def __init__(self, out_file: str):
        """Init with output log file."""
        self.terminal = sys.stdout
        reset_log = open(out_file, "w")
        reset_log.close()
        self.outfile = open(out_file, "a")

    def write(self, message: str):
        """Write message to both terminal and output log file.

        Args:
            message: A string message to be written.
        """
        self.terminal.write(message)
        self.outfile.write(message)

    def flush(self):
        """Allow flush."""
        pass

    @classmethod
    def start(cls, out_file: str):
        """Start writing to both terminal and output log file."""
        sys.stdout = Logger(out_file)

    @classmethod
    def stop(cls):
        """Stop writing to both terminal and output log file."""
        sys.stdout.outfile.close()
        sys.stdout = sys.stdout.terminal


def receive_args():
    """Receive command line arguments.

    Args:
        None

    Returns:
        A bool indicating if output should be verbose.
        A string representing filepath to optional output log file.
        A string representing filepath to input source program file.
    """
    arg_parser = argparse.ArgumentParser(
        description="""Simple syntax and static semantic analyzer for TinyAda.
Parse source program and report any syntax, lexical or static semantic errors.""",
        epilog="""Created by team 5 (Kim JM, Kim JH, Ma JY)
Programming Language Structures (CSI3103)""",
        formatter_class=argparse.RawTextHelpFormatter)
    arg_parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="more verbose output")
    arg_parser.add_argument(
        "-o", "--output",
        help="file to save output")
    arg_parser.add_argument(
        "input", help="filepath to source program file")
    args = arg_parser.parse_args()
    return args.input, args.output, args.verbose


if __name__ == '__main__':
    in_file, out_file, is_verbose = receive_args()
    if out_file:
        Logger.start(out_file)
    cur_chario = chario.Chario(in_file, is_verbose)
    cur_scanner = scanner.Scanner(cur_chario)
    cur_parser = parser7.Parser(cur_chario, cur_scanner)
    try:
        cur_parser.compilation()
    except Exception:
        cur_chario.report_errors()
    if out_file:
        Logger.stop()
