import argparse

from new_parser import parse_file
from new_interpreter import interpret_ast

parser = argparse.ArgumentParser()
parser.add_argument('filename')

args = parser.parse_args()

ast = parse_file(args.filename)

interpret_ast(ast)