import argparse

from parser import parse_file
from interpreter import interpret_ast

parser = argparse.ArgumentParser()
parser.add_argument('filename')

args = parser.parse_args()

ast = parse_file(args.filename)

interpret_ast(ast)