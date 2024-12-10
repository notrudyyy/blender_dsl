import bpy
import numpy as np
from lark import Tree, Token

# Import the specific functions
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

class BlenderASTInterpreter:
    def __init__(self):
        """
        Initialize the AST interpreter
        """
        self.symbol_table = {}

    def interpret(self, ast):
        """
        Main interpretation method for the entire AST
        """
        if not isinstance(ast, Tree) or ast.data != 'start':
            raise ValueError("Invalid AST structure")
        
        # Process each expression in the AST
        results = []
        for expr in ast.children:
            print("EXP: ", expr)
            result = self.interpret_expression(expr)
            print("RESULT: ", result)
            if result is not None:
                results.append(result)
        
        return results

    def interpret_expression(self, expr):
        """
        Interpret individual expressions
        """
        if not isinstance(expr, Tree) or expr.data != 'expression':
            raise ValueError("Invalid expression structure")
        
        # The first child is the operation type
        operation = expr.children[0]
        operation_type = operation.type
        print("OP: ", operation)
        print("OP_VAL: ", operation.value)
        print("OP_TYPE: ", operation.type)
        # Match against the specific grammar rules
        if operation.value == 'create':
            return self.interpret_create(expr.children)
        
        elif operation.value == 'operation':
            return self.interpret_operation(expr.children)
        
        elif operation.value == 'save':
            return self.save_scene(self.parse_value(expr.children[1]))
        
        elif operation.value == 'let':
            # Two variants: let VAR arithmetic or let VAR input
            return self.interpret_let(expr.children)
        
        return None

    def interpret_create(self, children):
        """
        Interpret create operations
        """
        # Extract create keyword, thing type, and parameters
        create_keyword = children[0]
        thing_type = children[1].value
        params = self.extract_params(children[2])
        
        # Prepare parameters
        parsed_params = {}
        for param_name, param_value in params.items():
            print("Parsing: ", param_value)
            parsed_params[param_name] = self.parse_value(param_value)
            print("Result: ", parsed_params[param_name])
        print(parsed_params)

        # Dispatch to appropriate creation method
        if thing_type == 'object':
            _create_object(**parsed_params)
        
        elif thing_type == 'collection':
            
            _create_collection(**parsed_params)
        
        elif thing_type == 'light':
            # Default to point light
            _create_light(**parsed_params)
        
        elif thing_type == 'camera':
            _create_camera(**parsed_params)
        
        return None

    def interpret_operation(self, children):
        """
        Interpret transform or other operations

        syntax: 
        """
        # Extract operation details
        operation_type = children[1]
        params = self.extract_params(children[2])
        print("OP_TYPE: ", operation_type)
        # print(params)
        
        # Prepare parameters
        parsed_params = {}
        for param_name, param_value in params.items():
            print("PARAM NAME: ", param_name)
            print("Parsing: ", param_value)
            parsed_params[param_name] = self.parse_value(param_value)
            print("Result: ", parsed_params[param_name])
        print(parsed_params)
            
        
        # Dispatch to appropriate transformation method
        if operation_type == 'transform':
            # Determine transform type (translate/rotate/scale)
            if 'location' in parsed_params:
                _transform_object(type='translate', **parsed_params)
            elif 'rotation' in parsed_params:
                _transform_object(type='rotate', **parsed_params)
            elif 'scale' in parsed_params:
                _transform_object(type='scale', **parsed_params)
        
        return None

    def interpret_let(self, children):
        """
        Interpret variable assignment
        """
        print(children)
        var_name = children[1]
        value = self.parse_value(children[2])
    
        # Store in symbol table
        self.symbol_table[var_name] = value
        
        return None

    def extract_params(self, params_tree):
        """
        Extract parameters from the AST params tree
        """
        if not isinstance(params_tree, Tree) or params_tree.data != 'params':
            return {}
        
        param_dict = {}
        for param in params_tree.children:
            # Each param is a Tree with 'param' data
            if isinstance(param, Tree) and param.data == 'param':
                # Extract parameter name and value
                param_name = param.children[0].value
                param_value = param.children[2]
                param_dict[param_name] = param_value
        
        return param_dict

    def parse_value(self, value):
        """
        Parse different types of values from the AST
        """
        print("IN PARSE VALUE: ", value)
        if isinstance(value, Token):
            print("+++++++++++++++++++++++++")
            # print("VALUE: ", value)
            print("VALUE_DATA: ", value.type)
            # Direct tokens (strings, numbers)
            if value.type == 'STRING':
                return value.value.strip('"')
            elif value.type == 'FLOAT':
                return float(value.value)
            elif value.type == 'INTEGER':
                return int(value.value)
            elif value.type == '__ANON_4':
                return input(value.value)
            return value.value
        
        elif isinstance(value, Tree):
            print("---------------------")
            # print("VALUE: ", value)
            print("VALUE_DATA: ", value.data)
            # More complex structures like tuples or arithmetic
            if value.data == 'data':
                return self.parse_value(value.children[0])

            elif value.data == 'prim':
                print("PRIMMMITIVEE")
                # Primitive value
                return self.parse_value(value.children[0])
            
            elif value.data == 'tuple':
                print("TUPPLEEEEE")
                # Convert tuple elements
                # print("ELEMS: ", [self.parse_value(elem).strip('\'') for elem in value.children])
                print("TUPLE: ", tuple(self.parse_value(elem) for elem in value.children))
                return tuple(self.parse_value(elem) for elem in value.children)
            
            elif value.data == 'term':
                print("TERRRRMMM")
                return self.parse_value(value.children[0])
                        
            elif value.data == 'arithmetic':
                print("ARRRITTHHHMETIC")
                # Perform arithmetic operation
                left = self.parse_value(value.children[0])
                op = value.children[1]
                right = self.parse_value(value.children[2])

                print("L: ", left)
                print("R: ", right)
                if op == '+':
                    return left + right
                elif op == '-':
                    return left - right
                elif op == '*':
                    return left * right
                elif op == '/':
                    return left / right
                
            elif value.data == 'numeric':
                return self.parse_value(value.children[0])
            
            elif value.data == 'signed_numeric':
                if value.children[0] == None or value.children[0] == '+':
                    return self.parse_value(value.children[1])
                else:
                    return -self.parse_value(value.children[1])
        return value

    def save_scene(self, filep):
        """
        Save the current Blender scene
        """
        bpy.ops.wm.save_mainfile(filepath=filep+".blend")
        return None

def interpret_blender_ast(ast, print_st):
    """
    Top-level function to interpret a Blender AST
    """
    interpreter = BlenderASTInterpreter()
    interpreter.interpret(ast)
    
    if print_st:
        print(interpreter.symbol_table)

# Example usage would look like:
collection_creation = Tree(Token('RULE', 'start'), [Tree(Token('RULE', 'expression'), [Token('__ANON_0', 'create'), Token('THING', 'collection'), Tree(Token('RULE', 'params'), [Tree(Token('RULE', 'param'), [Token('VAR', 'name'), Token('EQUALS', '='), Tree(Token('RULE', 'data'), [Tree(Token('RULE', 'prim'), [Token('STRING', '"random_collection"')])])]), Tree(Token('RULE', 'param'), [Token('VAR', 'object_types'), Token('EQUALS', '='), Tree(Token('RULE', 'data'), [Tree(Token('RULE', 'tuple'), [Tree(Token('RULE', 'prim'), [Token('STRING', '"cube"')]), Tree(Token('RULE', 'prim'), [Token('STRING', '"sphere"')]), Tree(Token('RULE', 'prim'), [Token('STRING', '"cylinder"')])])])]), Tree(Token('RULE', 'param'), [Token('VAR', 'count'), Token('EQUALS', '='), Tree(Token('RULE', 'data'), [Tree(Token('RULE', 'tuple'), [Tree(Token('RULE', 'prim'), [Tree(Token('RULE', 'signed_numeric'), [None, Tree(Token('RULE', 'numeric'), [Token('INTEGER', '10')])])])])])]), Tree(Token('RULE', 'param'), [Token('VAR', 'placement'), Token('EQUALS', '='), Tree(Token('RULE', 'data'), [Tree(Token('RULE', 'prim'), [Token('STRING', '"sphere"')])])]), Tree(Token('RULE', 'param'), [Token('VAR', 'start_xyz'), Token('EQUALS', '='), Tree(Token('RULE', 'data'), [Tree(Token('RULE', 'tuple'), [Tree(Token('RULE', 'prim'), [Tree(Token('RULE', 'signed_numeric'), [None, Tree(Token('RULE', 'numeric'), [Token('INTEGER', '0')])])]), Tree(Token('RULE', 'prim'), [Tree(Token('RULE', 'signed_numeric'), [None, Tree(Token('RULE', 'numeric'), [Token('INTEGER', '0')])])]), Tree(Token('RULE', 'prim'), [Tree(Token('RULE', 'signed_numeric'), [None, Tree(Token('RULE', 'numeric'), [Token('INTEGER', '0')])])])])])]), Tree(Token('RULE', 'param'), [Token('VAR', 'sph_radius'), Token('EQUALS', '='), Tree(Token('RULE', 'data'), [Tree(Token('RULE', 'prim'), [Tree(Token('RULE', 'signed_numeric'), [None, Tree(Token('RULE', 'numeric'), [Token('FLOAT', '5.0')])])])])]), Tree(Token('RULE', 'param'), [Token('VAR', 'rand'), Token('EQUALS', '='), Tree(Token('RULE', 'data'), [Tree(Token('RULE', 'prim'), [Token('STRING', '"uniform"')])])])])]), Tree(Token('RULE', 'expression'), [Token('__ANON_2', 'save'), Token('STRING', '"nefile"')])])

object_creation = Tree(Token('RULE', 'start'), [Tree(Token('RULE', 'expression'), [Token('__ANON_0', 'create'), Token('THING', 'object'), Tree(Token('RULE', 'params'), [Tree(Token('RULE', 'param'), [Token('VAR', 'name'), Token('EQUALS', '='), Tree(Token('RULE', 'data'), [Tree(Token('RULE', 'prim'), [Token('STRING', '"green_sphere"')])])]), Tree(Token('RULE', 'param'), [Token('VAR', 'obj_type'), Token('EQUALS', '='), Tree(Token('RULE', 'data'), [Tree(Token('RULE', 'prim'), [Token('STRING', '"sphere"')])])]), Tree(Token('RULE', 'param'), [Token('VAR', 'location'), Token('EQUALS', '='), Tree(Token('RULE', 'data'), [Tree(Token('RULE', 'tuple'), [Tree(Token('RULE', 'prim'), [Tree(Token('RULE', 'signed_numeric'), [None, Tree(Token('RULE', 'numeric'), [Token('INTEGER', '4')])])]), Tree(Token('RULE', 'prim'), [Tree(Token('RULE', 'signed_numeric'), [None, Tree(Token('RULE', 'numeric'), [Token('INTEGER', '5')])])]), Tree(Token('RULE', 'prim'), [Tree(Token('RULE', 'signed_numeric'), [None, Tree(Token('RULE', 'numeric'), [Token('INTEGER', '6')])])])])])])])]), Tree(Token('RULE', 'expression'), [Token('__ANON_2', 'save'), Token('STRING', '"zfile"')])])

light_creation = Tree(Token('RULE', 'start'), [Tree(Token('RULE', 'expression'), [Token('__ANON_0', 'create'), Token('THING', 'light'), Tree(Token('RULE', 'params'), [Tree(Token('RULE', 'param'), [Token('VAR', 'name'), Token('EQUALS', '='), Tree(Token('RULE', 'data'), [Tree(Token('RULE', 'prim'), [Token('STRING', '"area_light"')])])]), Tree(Token('RULE', 'param'), [Token('VAR', 'type'), Token('EQUALS', '='), Tree(Token('RULE', 'data'), [Tree(Token('RULE', 'prim'), [Token('STRING', '"AREA"')])])]), Tree(Token('RULE', 'param'), [Token('VAR', 'location'), Token('EQUALS', '='), Tree(Token('RULE', 'data'), [Tree(Token('RULE', 'tuple'), [Tree(Token('RULE', 'prim'), [Tree(Token('RULE', 'signed_numeric'), [None, Tree(Token('RULE', 'numeric'), [Token('INTEGER', '0')])])]), Tree(Token('RULE', 'prim'), [Tree(Token('RULE', 'signed_numeric'), [None, Tree(Token('RULE', 'numeric'), [Token('INTEGER', '0')])])]), Tree(Token('RULE', 'prim'), [Tree(Token('RULE', 'signed_numeric'), [None, Tree(Token('RULE', 'numeric'), [Token('INTEGER', '5')])])])])])]), Tree(Token('RULE', 'param'), [Token('VAR', 'energy'), Token('EQUALS', '='), Tree(Token('RULE', 'data'), [Tree(Token('RULE', 'prim'), [Tree(Token('RULE', 'signed_numeric'), [None, Tree(Token('RULE', 'numeric'), [Token('INTEGER', '500')])])])])]), Tree(Token('RULE', 'param'), [Token('VAR', 'radius'), Token('EQUALS', '='), Tree(Token('RULE', 'data'), [Tree(Token('RULE', 'prim'), [Tree(Token('RULE', 'signed_numeric'), [None, Tree(Token('RULE', 'numeric'), [Token('FLOAT', '0.5')])])])])])])]), Tree(Token('RULE', 'expression'), [Token('__ANON_2', 'save'), Token('STRING', '"zfile"')])])

camera_creation = Tree(Token('RULE', 'start'), [Tree(Token('RULE', 'expression'), [Token('__ANON_0', 'create'), Token('THING', 'camera'), Tree(Token('RULE', 'params'), [Tree(Token('RULE', 'param'), [Token('VAR', 'name'), Token('EQUALS', '='), Tree(Token('RULE', 'data'), [Tree(Token('RULE', 'prim'), [Token('STRING', '"fixed_camera"')])])]), Tree(Token('RULE', 'param'), [Token('VAR', 'target_coord'), Token('EQUALS', '='), Tree(Token('RULE', 'data'), [Tree(Token('RULE', 'tuple'), [Tree(Token('RULE', 'prim'), [Tree(Token('RULE', 'signed_numeric'), [None, Tree(Token('RULE', 'numeric'), [Token('INTEGER', '0')])])]), Tree(Token('RULE', 'prim'), [Tree(Token('RULE', 'signed_numeric'), [None, Tree(Token('RULE', 'numeric'), [Token('INTEGER', '0')])])]), Tree(Token('RULE', 'prim'), [Tree(Token('RULE', 'signed_numeric'), [None, Tree(Token('RULE', 'numeric'), [Token('INTEGER', '0')])])])])])]), Tree(Token('RULE', 'param'), [Token('VAR', 'r'), Token('EQUALS', '='), Tree(Token('RULE', 'data'), [Tree(Token('RULE', 'prim'), [Tree(Token('RULE', 'signed_numeric'), [None, Tree(Token('RULE', 'numeric'), [Token('INTEGER', '15')])])])])]), Tree(Token('RULE', 'param'), [Token('VAR', 'theta'), Token('EQUALS', '='), Tree(Token('RULE', 'data'), [Tree(Token('RULE', 'prim'), [Tree(Token('RULE', 'signed_numeric'), [None, Tree(Token('RULE', 'numeric'), [Token('FLOAT', '0.785')])])])])]), Tree(Token('RULE', 'param'), [Token('VAR', 'phi'), Token('EQUALS', '='), Tree(Token('RULE', 'data'), [Tree(Token('RULE', 'prim'), [Tree(Token('RULE', 'signed_numeric'), [None, Tree(Token('RULE', 'numeric'), [Token('FLOAT', '0.785')])])])])])])]), Tree(Token('RULE', 'expression'), [Token('__ANON_2', 'save'), Token('STRING', '"zfile"')])])

operation_test = Tree(Token('RULE', 'start'), [Tree(Token('RULE', 'expression'), [Token('__ANON_1', 'operation'), Token('VAR', 'object'), Tree(Token('RULE', 'params'), [Tree(Token('RULE', 'param'), [Token('VAR', 'name'), Token('EQUALS', '='), Tree(Token('RULE', 'data'), [Tree(Token('RULE', 'prim'), [Token('STRING', '"rotate_sphere"')])])]), Tree(Token('RULE', 'param'), [Token('VAR', 'type'), Token('EQUALS', '='), Tree(Token('RULE', 'data'), [Tree(Token('RULE', 'prim'), [Token('STRING', '"rotate"')])])]), Tree(Token('RULE', 'param'), [Token('VAR', 'rotation'), Token('EQUALS', '='), Tree(Token('RULE', 'data'), [Tree(Token('RULE', 'tuple'), [Tree(Token('RULE', 'prim'), [Tree(Token('RULE', 'signed_numeric'), [None, Tree(Token('RULE', 'numeric'), [Token('INTEGER', '0')])])]), Tree(Token('RULE', 'prim'), [Tree(Token('RULE', 'signed_numeric'), [None, Tree(Token('RULE', 'numeric'), [Token('INTEGER', '45')])])]), Tree(Token('RULE', 'prim'), [Tree(Token('RULE', 'signed_numeric'), [None, Tree(Token('RULE', 'numeric'), [Token('INTEGER', '0')])])])])])])])]), Tree(Token('RULE', 'expression'), [Token('__ANON_2', 'save'), Token('STRING', '"zfile"')])])

# interpret_blender_ast(light_creation, 1)
interpret_blender_ast(operation_test, 1)

