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
    tester = 'create object (name="myobj", obj_type="cube") create object (name="spherey", obj_type="sphere") save "savefile"'
    print("Create test:", tester)
    ast1 = l.parse(tester)
    print(ast1)

    # Test operation with explicit 'operation' keyword
    tester = 'operation transform (target="cube", scale=(-1,-1,-1))'
    print("\nOperation test:", tester)
    ast2 = l.parse(tester)
    print(ast2)

    # Test save
    tester = 'save "savefile.txt"'
    print("\nSave test:", tester)
    ast3 = l.parse(tester)
    print(ast3)

    # Test let with arithmetic
    tester = 'let x 5 + 3'
    print("\nLet with arithmetic test:", tester)
    ast4 = l.parse(tester)
    print(ast4)

    # Test let with input
    tester = 'let username input("Enter username:")'
    print("\nLet with input test:", tester)
    ast5 = l.parse(tester)
    print(ast5)

    # Test complex create
    tester = 'create object (name="MyObject", position=(1.5, 2.0, 3.0), color="red")'
    print("\nComplex create test:", tester)
    ast6 = l.parse(tester)
    print(ast6)

    # Additional test cases
    tester = 'operation scale (factor=2)'
    print("\nAnother operation test:", tester)
    ast7 = l.parse(tester)
    print(ast7)

if __name__ == "__main__":
    test_parser()