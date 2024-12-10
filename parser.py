from lark import Lark

with open("grammar.lark") as f:
    l = Lark(f)

def parse_file(path: str):
    with open(path) as f:
        return l.parse(f.read())

# Examples of usage
def test_parser():
    # Test create
    tester = 'create object (name="myobj", obj_type="cube") create object (name="spherey", obj_type="sphere") save("savefile")'
    print("Create test:", tester)
    ast1 = l.parse(tester)
    print(ast1)

    # Test operation with explicit 'operation' keyword
    tester = 'operation transform (target="cube", scale=[-1,-1,-1])'
    print("\nOperation test:", tester)
    ast2 = l.parse(tester)
    print(ast2)

    # Test save
    tester = 'save("savefile.txt")'
    print("\nSave test:", tester)
    ast3 = l.parse(tester)
    print(ast3)

    # Test let with arithmetic
    tester = 'let x y + z'
    print("\nLet with arithmetic test:", tester)
    ast4 = l.parse(tester)
    print(ast4)

    # Test let with input
    tester = 'let username input("Enter username:", string)'
    print("\nLet with input test:", tester)
    ast5 = l.parse(tester)
    print(ast5)

    # Test complex create
    tester = 'create object (name="MyObject", position=[1.5, 2.0, 3.0], color="red")'
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