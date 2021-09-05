"""Command line user interface for syntax analyzer."""
import argparse
import fileinput
import sys
import os
import chario
import scanner
import parser6


class Logger(object):
    """Write log (result) to file

    Attributes:
        terminal: STDOUT
        out_file: file to write log
    """
    def __init__(self, out_file: str):
        """Init with out_file"""
        self.terminal = sys.stdout
        reset_log = open(out_file, "w")
        reset_log.close()
        self.outfile = open(out_file, "a")

    def write(self, message: str):
        """Write message in terminal and out_file

        Args:
            message: Message to be printed on terminal and written to out_file
        """
        self.terminal.write(message)
        self.outfile.write(message)

    def flush(self):
        """flush"""
        pass

    @classmethod
    def start(cls, out_file: str):
        """Start writing log to out_file"""
        sys.stdout = Logger(out_file)

    @classmethod
    def stop(cls):
        """End writing log to out_file"""
        sys.stdout.outfile.close()
        sys.stdout = sys.stdout.terminal


def receive_args():
    """Receive command line arguments.

    Args:
        None

    Returns:
        A bool indicating if the input is a file or stream.
        A list containing source program from a file or stream.
    """
    arg_parser = argparse.ArgumentParser(
        description="""Simple syntax analyzer for TinyAda.
        Parse source program and report any syntax or lexical errors.""",
        epilog="""Created by team 5 (Kim JM, Kim JH, Ma JY)
        Programming Language Structures (CSI3103)""",
        formatter_class=argparse.RawTextHelpFormatter)
    arg_parser.add_argument(
        "-f", "--file", action="store_true",
        help="Read source program file from filepath provided by input.")
    arg_parser.add_argument(
        "-o", "--output",
        help="File for storing program output.")
    arg_parser.add_argument(
        "input", nargs="*",
        help="Stream of source program or filepath to source program file.")
    args = arg_parser.parse_args()
    return args.file, args.output, args.input


if __name__ == '__main__':
    is_file_inp, out_file, inp = receive_args()
    if out_file:
        Logger.start(out_file)
    if is_file_inp:
        if os.path.isfile(inp):
            file_inp = open(inp)
            cur_chario = chario.Chario(file_inp)
            cur_scanner = scanner.Scanner(cur_chario)
            cur_parser = parser6.Parser(cur_chario, cur_scanner)
            try:
                cur_parser.compilation()
            except Exception as e:
                print(str(e))  # Debugging purpose
                cur_chario.report_errors()
            file_inp.close()
        else:
            print("E: Invalid filepath or faulty file: {}".format(inp))
    else:
        stream_inp = fileinput.input(inp)
        cur_chario = chario.Chario(stream_inp)
        cur_scanner = scanner.Scanner(cur_chario)
        cur_parser = parser6.Parser(cur_chario, cur_scanner)
        stream_inp.close()
    if out_file:
        Logger.stop()
