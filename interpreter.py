from bpy_wrapper import (
    _create_object, 
    _create_light, 
    _create_collection, 
    _create_camera,
    _hide_object, 
    _show_object, 
    _hide_collection, 
    _show_collection,
    _translate_object,
    _rotate_object,
    _scale_object,
    _translate_collection,
    _rotate_collection,
    _scale_collection,
    _save_scene,
    _remove_random_faces_object,
    _remove_random_faces_collection
)

from lark import Tree

from pathvalidate import is_valid_filename

create_types = {
    "object": _create_object,
    "light": _create_light,
    "collection": _create_collection,
    "camera": _create_camera,
}

operation_types = {
    "translate": {
        "object": _translate_object,
        "collection": _translate_collection,
    },
    "rotate": {
        "object": _rotate_object,
        "collection": _rotate_collection,
    },
    "scale": {
        "object": _scale_object,
        "collection": _scale_collection,
    },
    "hide": {
        "object": _hide_object,
        "collection": _hide_collection,
    },
    "show": {
        "object": _show_object,
        "collection": _show_collection,
    },
    "remove_faces": {
        "object": _remove_random_faces_object,
        "collection": _remove_random_faces_collection,
    }
}

env = {}

def interpret_ast(ast: Tree):
    if ast.data == "start":
        for child in ast.children:
            interpret_ast(child)
    elif ast.data == "expression":
        expression_type = ast.children[0]
        if expression_type == "create":
            create_type = ast.children[1]
            
            if create_type not in create_types:
                raise ValueError(f"{create_type} is not a valid thing that can be created!")

            create_params = interpret_ast(ast.children[2])

            create_types[create_type](**create_params)
        
        elif expression_type == "operation":
            operation_type = ast.children[1]
            
            if operation_type not in operation_types:
                raise ValueError(f"{operation_type} is not a valid operation!")
            
            operation_params = interpret_ast(ast.children[2])

            operation_target = operation_params["op_target"]

            del operation_params["op_target"]

            operation_types[operation_type][operation_target](**operation_params)
        
        elif expression_type == "save":
            save_file = interpret_ast(ast.children[1])

            if not is_valid_filename(save_file):
                raise ValueError(f"{save_file} is not a valid filename!")
            
            _save_scene(save_file)
        
        elif expression_type == "let":
            var_name = ast.children[1]
            
            if ast.children[2] == "input":
                type_cast = eval(ast.children[4].data)

                input_string = ast.children[3].data
                
                env[var_name] = type_cast(input(input_string))
            else:
                var_value = interpret_ast(ast.children[2])
                
                env[var_name] = var_value
    
    elif ast.data == "arithmetic":
        binary_op = ast.children[1].data
        
        lval = interpret_ast(ast.children[0])
        rval = interpret_ast(ast.children[2])

        return eval(f"{lval} {binary_op} {rval}")
    
    elif ast.data == "term":
        if type(ast.children[0]) == Tree:
            return interpret_ast(ast.children[0])
        var_name = ast.children[0]
        
        if var_name not in env:
            raise ValueError(f"{var_name} is not a valid identifier!")
        
        return env[var_name]
    
    elif ast.data == "params":
        param_dict = {}
        for param in ast.children:
            par, val = interpret_ast(param)
            param_dict[par] = val
        
        return param_dict
    
    elif ast.data == "param":
        return (ast.children[0], interpret_ast(ast.children[1]))
    
    elif ast.data == "data":
        return interpret_ast(ast.children[0])
    
    elif ast.data == "prim":
        if type(ast.children[0]) == Tree:
            return interpret_ast(ast.children[0])
        return ast.children[0]
    
    elif ast.data == "signed_numeric":
        sign = ast.children[0].data if ast.children[0] is not None else ""
        value = interpret_ast(ast.children[1])

        if sign == "-":
            return -value
        return value
    
    elif ast.data == "numeric":
        numeric_type = str(ast.children[0].type)

        if numeric_type == "FLOAT":
            return float(ast.children[0])
        return int(ast.children[0])
    
    elif ast.data == "tuple":
        if len(ast.children) == 0:
            return tuple()
        return tuple(interpret_ast(item) for item in ast.children)
    
    elif ast.data == "string":
        return ast.children[0][1:-1]