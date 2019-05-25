"""
The main command-line tool for maintaining the Boundless Recipes database
"""
import argparse
import sys
from . import load, recipe


COMMANDS = [
    load,
    recipe,
]


def main(args=None):
    """
    Command-line tool entry point
    """
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(prog='ptracker')
    parser.add_argument('-V', '--version',
                        action='version',
                        version='1.0')
    parser.add_argument('-v', '--verbose',
                        action='count', default=0,
                        help='increase logging verbosity')

    subparsers = parser.add_subparsers(title='commands')
    for command in COMMANDS:
        command.add_parser(subparsers)

    args = parser.parse_args(args)
    args.func(args)
    sys.exit(0)


if __name__ == '__main__':
    main()
