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


def test_blender_script():
    # Test cases for _create_collection
    test_collection_cases = [
        # Basic collection creation with uniform placement
        'create collection (name="basic_collection", object_types=("cube", "sphere"), count=(5,3), placement="linear", start_xyz=(0,0,0), lin_distance=2.0, lin_axis="x")',
        
        # Collection with random object selection
        'create collection (name="random_collection", object_types=("cube", "sphere", "cylinder"), count=(10), placement="sphere", start_xyz=(0,0,0), sph_radius=5.0, rand="uniform") save "zfile"',
        
        # Plane placement collection
        'create collection (name="plane_collection", object_types=("cube"), count=(8), placement="plane", plane_corner1=(-5,-5,0), plane_corner2=(5,5,0)) save "zfile"',
        
        # Circle placement collection
        'create collection (name="circle_collection", object_types=("sphere"), count=(6), placement="circle", start_xyz=(0,0,0), circle_exclude_axis="z", circle_radius=10.0) save "zfile"'
    ]

    # Test cases for _create_object
    test_object_cases = [
        'create object (name="red_cube", obj_type="cube", location=(1,2,3), scale=(2,2,2), rotation=(0,0,45), collection="test_collection") save "zfile"',
        'create object (name="green_sphere", obj_type="sphere", location=(4,5,6)) save "zfile"'
    ]

    # Test cases for _create_light
    test_light_cases = [
        'create light (name="main_light", type="POINT", location=(10,10,10), energy=1500, color=(1,0.8,0.6)) save "zfile"',
        'create light (name="area_light", type="AREA", location=(0,0,5), energy=500, radius=0.5) save "zfile"'
    ]

    # Test cases for _create_camera
    test_camera_cases = [
        'create camera (name="scene_camera", target_collection="main_scene", r=20, theta=45, phi=30) save "zfile"',
        'create camera (name="fixed_camera", target_coord=(0,0,0), r=15, theta=0.785, phi=0.785) save "zfile"'
    ]

    # Test cases for object transformations
    test_transform_cases = [
        'operation transform (name="move_cube", type="translate", location=(1,2,3)) save "zfile"',
        'operation transform (name="rotate_sphere", type="rotate", rotation=(0,45,0)) save "zfile"',
        'operation collection (name="move_group", type="scale", scale=(1.5,1.5,1.5)) save "zfile"'
    ]

    # Test cases for object/collection visibility
    test_visibility_cases = [
        'operation object (name="hide_cube", type="hide", viewport=true, render=false) save "zfile"',
        'operation collection (name="hide_group", type="show", viewport=true, render=true) save "zfile"'
    ]

    # Test case for face removal
    test_face_removal_cases = [
        'operation object (name="damage_cube", type="remove_faces", removal_percentage=0.3) save "zfile"',
        'operation collection (name="damaged_group", type="remove_faces", removal_percentage=0.5) save "zfile"'
    ]

    # Test case for saving scene
    test_save_case = 'save "final_scene.blend"'

    # Combine all test cases
    all_test_cases = (
        test_collection_cases + 
        test_object_cases + 
        test_light_cases + 
        test_camera_cases + 
        test_transform_cases + 
        test_visibility_cases + 
        test_face_removal_cases + 
        [test_save_case]
    )

    testcase = test_collection_cases[1]
    print("input= ", testcase)
    print(l.parse(testcase))
    testcase = test_object_cases[1]
    print("input= ", testcase)
    print(l.parse(testcase))
    testcase = test_light_cases[1]
    print("input= ", testcase)
    print(l.parse(testcase))
    testcase = test_camera_cases[1]
    print("input= ", testcase)
    print(l.parse(testcase))
    testcase = test_transform_cases[1]
    print("input= ", testcase)
    print(l.parse(testcase))

    # Parse and print each test case

    # for test_case in all_test_cases:
    #     print(f"Testing: {test_case}")
    #     try:
    #         ast = l.parse(test_case)
    #         print("Parse successful:", ast)
    #     except Exception as e:
    #         print("Parse failed:", e)


if __name__ == "__main__":
    test_blender_script()