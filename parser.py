import bpy
import numpy as np
import inspect
# from main import all
from typing import List, Union, Callable, Optional
# Import the original functions to make them available
from main import (
    _create_object, 
    _create_light, 
    _create_collection, 
    _create_camera,
    _hide_object, 
    _show_object, 
    _hide_collection, 
    _show_collection
)


# def set_default(category: str, **kwargs):
#     """
#     Set default parameters for various scene elements
    
#     Examples:
#     - set_default('camera', distance=20, theta=np.pi/2)
#     - set_default('light', type='SUN', energy=500, color=(1,0,0))
#     """
#     if category == 'camera':
#         self._default_camera.update(kwargs)
#     elif category == 'light':
#         self._default_light.update(kwargs)
#     else:
#         raise ValueError(f"Unsupported default category: {category}")


#!what about phi and theta
def create_camera(
    name: str | None,
    target_collection: str = None,
    distance=10,
):
    _create_camera(
        name=name,
        target_collection=target_collection,
        r=distance,
    )

class create_object:
   @staticmethod
   def cube(
       name: str,
       location: tuple = (0,0,0),
       scale: tuple = (1,1,1),
       rotation: tuple = (0,0,0),
       collection: str = None
   ):
       filtered_kwargs = {k: v for k, v in locals().items() 
                          if k not in ['name'] and v is not None}
       _create_object(name=name, obj_type="cube", **filtered_kwargs)

   @staticmethod
   def sphere(
       name: str,
       location: tuple = (0,0,0),
       scale: tuple = (1,1,1),
       rotation: tuple = (0,0,0),
       collection: str = None
   ):
       filtered_kwargs = {k: v for k, v in locals().items() 
                          if k not in ['name'] and v is not None}
       _create_object(name=name, obj_type="sphere", **filtered_kwargs)

   @staticmethod
   def cylinder(
       name: str,
       location: tuple = (0,0,0),
       scale: tuple = (1,1,1),
       rotation: tuple = (0,0,0),
       collection: str = None
   ):
       filtered_kwargs = {k: v for k, v in locals().items() 
                          if k not in ['name'] and v is not None}
       _create_object(name=name, obj_type="cylinder", **filtered_kwargs)

   @staticmethod
   def cone(
       name: str,
       location: tuple = (0,0,0),
       scale: tuple = (1,1,1),
       rotation: tuple = (0,0,0),
       collection: str = None
   ):
       filtered_kwargs = {k: v for k, v in locals().items() 
                          if k not in ['name'] and v is not None}
       _create_object(name=name, obj_type="cone", **filtered_kwargs)

   @staticmethod
   def plane(
       name: str,
       location: tuple = (0,0,0),
       scale: tuple = (1,1,1),
       rotation: tuple = (0,0,0),
       collection: str = None
   ):
       filtered_kwargs = {k: v for k, v in locals().items() 
                          if k not in ['name'] and v is not None}
       _create_object(name=name, obj_type="plane", **filtered_kwargs)

   @staticmethod
   def create_object(
       obj_type: str,
       name: str,
       location: tuple = (0,0,0),
       scale: tuple = (1,1,1),
       rotation: tuple = (0,0,0),
       collection: str = None
   ):
       filtered_kwargs = {k: v for k, v in locals().items() 
                          if k not in ['name', 'obj_type'] and v is not None}
       _create_object(name=name, obj_type=obj_type, **filtered_kwargs)

#!for light, doing defualt setting in parser(can remove from inside), set energy=10 for sun(couldnt see color w 1000)
class create_light:
   
    def point(
        name: str,
        location: tuple = (0,0,0),
        energy: float = 1000,
        color: tuple = (1,1,1),
        radius: float = 0.1,
        collection: str = None
    ):
        
        _create_light(name=name, 
                      type="POINT", 
                      location=location, 
                      energy=energy,
                      color=color,
                      radius=radius,
                      collection=collection)
        
    def area(
        name: str,
        location: tuple = (0,0,0),
        energy: float = 1000,
        color: tuple = (1,1,1),
        radius: float = 0.1,
        collection: str = None
    ):
        
        _create_light(name=name, 
                      type="AREA", 
                      location=location, 
                      energy=energy,
                      color=color,
                      radius=radius,
                      collection=collection)
        
    def spot(
        name: str,
        location: tuple = (0,0,0),
        energy: float = 1000,
        color: tuple = (1,1,1),
        radius: float = 0.1,
        collection: str = None
    ):
        
        _create_light(name=name, 
                      type="SPOT", 
                      location=location, 
                      energy=energy,
                      color=color,
                      radius=radius,
                      collection=collection)
        
    def sun(
        name: str,
        location: tuple = (0,0,0),
        energy: float = 10,
        color: tuple = (1,1,1),
        radius: float = 0.1,
        collection: str = None
    ):
        
        _create_light(name=name, 
                      type="SUN", 
                      location=location, 
                      energy=energy,
                      color=color,
                      radius=radius,
                      collection=collection)

def create_collection(
    name: str,
    object_types: list,
    count: list,
    placement: str,
    rand: str = None,
    start_xyz: list = None,
    lin_distance: float = None,
    lin_axis: str = None,
    lin_noisy_offset: float = None,
    weights: list = None,
    sph_radius: float = None,
    plane_corner1: list = None,
    plane_corner2: list = None,
    circle_radius: float = None,
    circle_exclude_axis: str = None,
):
    filtered_kwargs = {k: v for k, v in locals().items() 
                          if k not in ['name'] and v is not None}
    print(object_types)
    _create_collection(
        name=name,
        **filtered_kwargs,
    )
    
  

# def transform(
#                 object_name: Optional[str] = None, 
#                 collection: Optional[str] = None,
#                 translate: Optional[tuple] = None,
#                 rotate: Optional[tuple] = None,
#                 scale: Optional[tuple] = None,
#                 filter_func: Optional[Callable] = None):

def hide_object(name: str, viewport: bool = True, render: bool = True):
   _hide_object(name, viewport, render)

def hide_collection(name: str, viewport: bool = True, render: bool = True):
   _hide_collection(name, viewport, render)

def show_object(name: str, viewport: bool = True, render: bool = True):
   _show_object(name, viewport, render)

def show_collection(name: str, viewport: bool = True, render: bool = True):
   _show_collection(name, viewport, render)   

def save(fp: str):
    """
    Save the current Blender file
    
    Example:
    - save('./my_scene.blend')
    """
    bpy.ops.wm.save_mainfile(filepath= fp)

create_object.cube('dabox', location=(5, 6, 7), scale=(0.5, 0.5, 0.5))
create_light.area(name="myarea", location=(3, 0, 0), radius=5)
create_light.spot(name="myspot", location=(15, 15, -2), color=(5, 10, 0))
create_light.sun(name="myson", location=(9, 9, 0), color=(5, 0, 3))
create_collection(name='stuff', object_types=["cone", "sphere"], count=[2, 3], placement='sphere', start_xyz=(10, 10, -10), sph_radius=5)
# create_camera("mycam", target_collection='stuff', distance=3)
_create_camera(name='fixedcam', target_collection='stuff', theta= np.pi/4, phi= np.pi/4, r= 30)
# bpy.ops.wm.save_mainfile(filepath="./scene.blend")
save("./scene.blend")