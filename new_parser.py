from main import (
    _create_object, 
    _create_light, 
    _create_collection, 
    _create_camera,
    _hide_object, 
    _show_object, 
    _hide_collection, 
    _show_collection,
    _transform_object,
    _transform_collection,
)

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('filename')

args = parser.parse_args()

from lark import Lark

with open("grammar.lark") as f:
    l = Lark(f)

# Examples of usage
def test_parser():
    # Test create
    print("Create test:")
    ast1 = l.parse('create collection (name="myCollection")')
    print(ast1)

    # Test operation with explicit 'operation' keyword
    print("\nOperation test:")
    ast2 = l.parse('operation transform (target="cube", offset=(-1,-1,-1))')
    print(ast2)

    # Test save
    print("\nSave test:")
    ast3 = l.parse('save')
    print(ast3)

    # Test let with arithmetic
    print("\nLet with arithmetic test:")
    ast4 = l.parse('let x 5 + 3')
    print(ast4)

    # Test let with input
    print("\nLet with input test:")
    ast5 = l.parse('let username input("Enter username:")')
    print(ast5)

    # Test complex create
    print("\nComplex create test:")
    ast6 = l.parse('create object (name="MyObject", position=(1.5, 2.0, 3.0), color="red")')
    print(ast6)

    # Additional test cases
    print("\nAnother operation test:")
    ast7 = l.parse('operation scale (factor=2)')
    print(ast7)

if __name__ == "__main__":
    test_parser()