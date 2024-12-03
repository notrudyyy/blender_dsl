# concrete syntax

#set default orientation, camera

create_object.prim_id(object_type: str, 
                    name: str = None, 
                    location: tuple = (0,0,0), 
                    scale: tuple = (1,1,1),
                    rotation: tuple = (0,0,0))

create_light.type(name, location, dir, size)

create_collection(name, object_type[], count[], rand)

transform.type(object_name,translation: tuple = None, 
                          rotation: tuple = None, 
                          scale: tuple = None,
                          filter_func: Callable = None)

hide(object_name)
show(object_name)
save(file)

#parser 


import bpy
from typing import List, Union, Callable
from dataclasses import dataclass, field

#global collection and context 
    # Core collections and management
collections = {}

def create_collection(name: str, object_type: list, count: list, rand: str, placement: str, weights: list = None):
    """
    Create a new collection and optionally set it as the current working collection
    """
    collection = bpy.data.collections.new(name)
    # bpy.context.scene.collection.children.link(collection)
    if (len(count) != len(object_type)):
        if len(count) != 1:
            raise ValueError
        if rand:
            for i in range(count[0]):
                create_object(type=rand(object_type, weights=weights), name = None, collection = name)
        else:
            for obj_type in object_type:
                for i in range(count[0]):
                    create_object(obj_type=obj_type, name=None, collection = name)
                
    for obj_type, cnt in zip(object_type, count):
        for i in range(cnt):
            create_object(obj_type=obj_type, name=None, collection = name)

    collections[name] = collection

def create_object(obj_type: str, name: None | str, location: tuple = (0,0,0), scale: tuple = (1,1,1), rotation: tuple = (0,0,0)):
    """
    Add an object to the current collection with flexible creation options
    """

    # Mapping of object creation methods
    object_creators = {
        'cube': bpy.ops.mesh.primitive_cube_add,
        'sphere': bpy.ops.mesh.primitive_uv_sphere_add,
        'cylinder': bpy.ops.mesh.primitive_cylinder_add,
        'cone': bpy.ops.mesh.primitive_cone_add,
        'plane': bpy.ops.mesh.primitive_plane_add
    }

    if obj_type not in object_creators:
        raise ValueError(f"Unsupported object obj_type: {obj_type}")

    # Create the object
    object_creators[object_type](
        location=location, 
        scale=scale
    )

    # Get the most recently created object
    obj = bpy.context.active_object
    
    # Set name if provided
    if name:
        obj.name = name

    # Set rotation
    obj.rotation_euler = rotation

    # Link to current collection
    self.current_collection.objects.link(obj)
    
    return self

def apply_material(self, 
                    color: tuple = (1,1,1,1), 
                    metallic: float = 0.0, 
                    roughness: float = 0.5):
    """
    Apply a material to the currently selected object
    """
    material = bpy.data.materials.new(name="CustomMaterial")
    material.use_nodes = True
    
    # Access principled BSDF node
    nodes = material.node_tree.nodes
    principled_node = nodes.get("Principled BSDF")
    
    if principled_node:
        principled_node.inputs['Base Color'].default_value = color
        principled_node.inputs['Metallic'].default_value = metallic
        principled_node.inputs['Roughness'].default_value = roughness

    # Assign material to active object
    bpy.context.active_object.data.materials.append(material)
    
    return self

def transform_objects(self, 
                        translation: tuple = None, 
                        rotation: tuple = None, 
                        scale: tuple = None,
                        filter_func: Callable = None):
    """
    Apply transformations to objects in the current collection
    Optionally filter objects using a custom function
    """
    objects = self.current_collection.objects
    
    if filter_func:
        objects = [obj for obj in objects if filter_func(obj)]
    
    for obj in objects:
        if translation:
            obj.location += translation
        if rotation:
            obj.rotation_euler.rotate_axis += rotation
        if scale:
            obj.scale *= scale
    
    return self

def batch_duplicate(self, 
                    count: int, 
                    pattern: str = 'linear', 
                    offset: tuple = (1,0,0)):
    """
    Batch duplicate objects with different placement strategies
    """
    objects = list(self.current_collection.objects)
    
    for i in range(count):
        for obj in objects:
            new_obj = obj.copy()
            new_obj.data = obj.data.copy()
            
            if pattern == 'linear':
                new_obj.location = obj.location + (offset[0] * (i+1), 
                                                    offset[1] * (i+1), 
                                                    offset[2] * (i+1))
            elif pattern == 'radial':
                # Implement radial distribution logic
                pass
            
            self.current_collection.objects.link(new_obj)
    
    return self

# Example usage demonstration
def example_scene_creation():
    builder = BlenderSceneBuilder()
    
    (builder
        .create_collection("SceneParts")
        .add_object('cube', 'MainCube')
        .apply_material(color=(1,0,0,1), metallic=0.5)
        .batch_duplicate(3)
        .transform_objects(translation=(0,2,0))
    )

# Optional: Add a context manager for more Pythonic usage
class BlenderScene:
    def __init__(self):
        self.builder = BlenderSceneBuilder()
    
    def __enter__(self):
        return self.builder
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Optional cleanup or finalization
        pass