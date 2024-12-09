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
            if len(expr.children) == 3:
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
            light_type = parsed_params.get('type', 'POINT').upper()
            _create_light(type=light_type, **parsed_params)
        
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
        if isinstance(value, Token):
            # Direct tokens (strings, numbers)
            if value.type == 'STRING':
                return value.value.strip('"')
            elif value.type in ['FLOAT', 'INTEGER']:
                return float(value.value)
            return value.value
        
        elif isinstance(value, Tree):
            print("---------------------")
            print(value.data)
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
                print("TUPLE: ", tuple(self.parse_value(elem) for elem in value.children))
                return tuple(self.parse_value(elem) for elem in value.children)
            
            elif value.data == 'arithmetic':
                print("ARRRITTHHHMETIC")
                # Perform arithmetic operation
                left = self.parse_value(value.children[0])
                op = value.children[1]
                right = self.parse_value(value.children[2])
                
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

def interpret_blender_ast(ast):
    """
    Top-level function to interpret a Blender AST
    """
    interpreter = BlenderASTInterpreter()
    return interpreter.interpret(ast)

# Example usage would look like:
ast_1 = Tree(Token('RULE', 'start'), [Tree(Token('RULE', 'expression'), [Token('__ANON_0', 'create'), Token('THING', 'collection'), Tree(Token('RULE', 'params'), [Tree(Token('RULE', 'param'), [Token('VAR', 'name'), Token('EQUALS', '='), Tree(Token('RULE', 'data'), [Tree(Token('RULE', 'prim'), [Token('STRING', '"myCollection"')])])])])])])
ast_2 = Tree(Token('RULE', 'start'), [Tree(Token('RULE', 'expression'), [Token('__ANON_1', 'operation'), Token('VAR', 'transform'), Tree(Token('RULE', 'params'), [Tree(Token('RULE', 'param'), [Token('VAR', 'target'), Token('EQUALS', '='), Tree(Token('RULE', 'data'), [Tree(Token('RULE', 'prim'), [Token('STRING', '"cube"')])])]), Tree(Token('RULE', 'param'), [Token('VAR', 'scale'), Token('EQUALS', '='), Tree(Token('RULE', 'data'), [Tree(Token('RULE', 'tuple'), [Tree(Token('RULE', 'prim'), [Tree(Token('RULE', 'signed_numeric'), [Token('SIGN', '-'), Tree(Token('RULE', 'numeric'), [Token('INTEGER', '1')])])]), Tree(Token('RULE', 'prim'), [Tree(Token('RULE', 'signed_numeric'), [Token('SIGN', '-'), Tree(Token('RULE', 'numeric'), [Token('INTEGER', '1')])])]), Tree(Token('RULE', 'prim'), [Tree(Token('RULE', 'signed_numeric'), [Token('SIGN', '-'), Tree(Token('RULE', 'numeric'), [Token('INTEGER', '1')])])])])])])])])])
ast_3 = Tree(Token('RULE', 'start'), [Tree(Token('RULE', 'expression'), [Token('__ANON_2', 'save')])])
ast_4 = Tree(Token('RULE', 'start'), [Tree(Token('RULE', 'expression'), [Token('__ANON_3', 'let'), Token('VAR', 'x'), Tree(Token('RULE', 'arithmetic'), [Tree(Token('RULE', 'term'), [Tree(Token('RULE', 'signed_numeric'), [None, Tree(Token('RULE', 'numeric'), [Token('INTEGER', '5')])])]), Token('PLUS', '+'), Tree(Token('RULE', 'term'), [Tree(Token('RULE', 'signed_numeric'), [None, Tree(Token('RULE', 'numeric'), [Token('INTEGER', '3')])])])])])])
ast_5 = Tree(Token('RULE', 'start'), [Tree(Token('RULE', 'expression'), [Token('__ANON_3', 'let'), Token('VAR', 'username'), Token('__ANON_4', 'input'), Token('STRING', '"Enter username:"')])])
ast_6 = Tree(Token('RULE', 'start'), [Tree(Token('RULE', 'expression'), [Token('__ANON_0', 'create'), Token('THING', 'object'), Tree(Token('RULE', 'params'), [Tree(Token('RULE', 'param'), [Token('VAR', 'name'), Token('EQUALS', '='), Tree(Token('RULE', 'data'), [Tree(Token('RULE', 'prim'), [Token('STRING', '"MyObject"')])])]), Tree(Token('RULE', 'param'), [Token('VAR', 'position'), Token('EQUALS', '='), Tree(Token('RULE', 'data'), [Tree(Token('RULE', 'tuple'), [Tree(Token('RULE', 'prim'), [Tree(Token('RULE', 'signed_numeric'), [None, Tree(Token('RULE', 'numeric'), [Token('FLOAT', '1.5')])])]), Tree(Token('RULE', 'prim'), [Tree(Token('RULE', 'signed_numeric'), [None, Tree(Token('RULE', 'numeric'), [Token('FLOAT', '2.0')])])]), Tree(Token('RULE', 'prim'), [Tree(Token('RULE', 'signed_numeric'), [None, Tree(Token('RULE', 'numeric'), [Token('FLOAT', '3.0')])])])])])]), Tree(Token('RULE', 'param'), [Token('VAR', 'color'), Token('EQUALS', '='), Tree(Token('RULE', 'data'), [Tree(Token('RULE', 'prim'), [Token('STRING', '"red"')])])])])])])
ast_7 = Tree(Token('RULE', 'start'), [Tree(Token('RULE', 'expression'), [Token('__ANON_1', 'operation'), Token('VAR', 'scale'), Tree(Token('RULE', 'params'), [Tree(Token('RULE', 'param'), [Token('VAR', 'factor'), Token('EQUALS', '='), Tree(Token('RULE', 'data'), [Tree(Token('RULE', 'prim'), [Tree(Token('RULE', 'signed_numeric'), [None, Tree(Token('RULE', 'numeric'), [Token('INTEGER', '2')])])])])])])])])
ast_8 = Tree(Token('RULE', 'start'), [Tree(Token('RULE', 'expression'), [Token('__ANON_0', 'create'), Token('THING', 'object'), Tree(Token('RULE', 'params'), [Tree(Token('RULE', 'param'), [Token('VAR', 'name'), Token('EQUALS', '='), Tree(Token('RULE', 'data'), [Tree(Token('RULE', 'prim'), [Token('STRING', '"myobj"')])])]), Tree(Token('RULE', 'param'), [Token('VAR', 'obj_type'), Token('EQUALS', '='), Tree(Token('RULE', 'data'), [Tree(Token('RULE', 'prim'), [Token('STRING', '"cube"')])])])])]), Tree(Token('RULE', 'expression'), [Token('__ANON_0', 'create'), Token('THING', 'object'), Tree(Token('RULE', 'params'), [Tree(Token('RULE', 'param'), [Token('VAR', 'name'), Token('EQUALS', '='), Tree(Token('RULE', 'data'), [Tree(Token('RULE', 'prim'), [Token('STRING', '"spherey"')])])]), Tree(Token('RULE', 'param'), [Token('VAR', 'obj_type'), Token('EQUALS', '='), Tree(Token('RULE', 'data'), [Tree(Token('RULE', 'prim'), [Token('STRING', '"sphere"')])])])])]), Tree(Token('RULE', 'expression'), [Token('__ANON_2', 'save'), Token('STRING', '"savefile"')])])


interpret_blender_ast(ast_8)