import bpy
import random
import numpy as np
import math
import mathutils

for obj in bpy.data.objects:
    bpy.data.objects.remove(obj)

collections = {}

def __uniform_sampler(items: list, weights: list):
    return random.sample(items, 1)[0]

def __weighted_sampler(items: list, weights: list):
    return random.choices(items, weights=weights, k=1)[0]

def __calc_center_pt(mesh_objs):
    minA = np.full((3,), np.inf)
    maxB = np.full((3,), -np.inf)
    
    for ob in mesh_objs:
        default_corner = np.ndarray((4,))
        default_corner[3] = 1.0
        bbox_corners = []
        for corner in ob.bound_box:
            default_corner[:3] = corner
            bbox_corners.append(np.array(ob.matrix_world) @ default_corner)
        minA = np.min(np.vstack((minA, bbox_corners[0][:3])), 0)
        maxB = np.max(np.vstack((maxB, bbox_corners[6][:3])), 0)

    center_point = (minA+maxB)/2
    return center_point

def _create_camera(
    name: str | None = None,
    target_coord: list | None = None,
    target_collection: str | None = None,
    r: float = 10,
    theta: float = 0,
    phi: float = 0,
):
    """
    Create a camera positioned using spherical coordinates relative to a target.
    
    Args:
        name: Optional name for the camera
        target_coord: Target coordinate to point the camera towards
        target_collection: Alternatively, specify a collection to calculate center point
        r: Radius (distance from target)
        theta: Azimuthal angle in the x-y plane from the x-axis (in degrees)
        phi: Polar angle from the z-axis (in degrees)
    
    Returns:
        bpy.types.Object: Created camera object
    """
    # Validate input
    if bool(target_collection) == bool(target_coord):
        raise ValueError("Exactly one of target_collection or target_coord must be specified")
    
    # Calculate target coordinate if collection is provided
    if target_collection:
        target_coord = __calc_center_pt(
            mesh_objs=[obj for obj in bpy.data.collections[target_collection].all_objects if obj.type == "MESH"]
        )
    
    phi = (phi%360)*math.pi/180
    theta = (theta%360)*math.pi/180

    # Calculate camera position using spherical coordinates
    x = target_coord[0] + r * math.sin(phi) * math.cos(theta)
    y = target_coord[1] + r * math.sin(phi) * math.sin(theta)
    z = target_coord[2] + r * math.cos(phi)
    
    # Create camera
    bpy.ops.object.camera_add(
        location=(x, y, z),
        enter_editmode=False,
    )
    
    # Get the camera object
    camera = bpy.context.active_object
    
    # Set name if provided
    if name:
        camera.name = name

    def point_at(obj, target, roll=0):
        """
        Rotate obj to look at target

        :arg obj: the object to be rotated. Usually the camera
        :arg target: the location (3-tuple or Vector) to be looked at
        :arg roll: The angle of rotation about the axis from obj to target in radians. 

        Based on: https://blender.stackexchange.com/a/5220/12947 (ideasman42)      
        """
        if not isinstance(target, mathutils.Vector):
            target = mathutils.Vector(target)
        loc = obj.location
        # direction points from the object to the target
        direction = target - loc
        tracker, rotator = (('-Z', 'Y'),'Z') if obj.type=='CAMERA' else (('X', 'Z'),'Y') #because new cameras points down(-Z), usually meshes point (-Y)
        quat = direction.to_track_quat(*tracker)
        
        # /usr/share/blender/scripts/addons/add_advanced_objects_menu/arrange_on_curve.py
        quat = quat.to_matrix().to_4x4()
        rollMatrix = mathutils.Matrix.Rotation(roll, 4, rotator)

        # remember the current location, since assigning to obj.matrix_world changes it
        loc = loc.to_tuple()
        #obj.matrix_world = quat * rollMatrix
        # in blender 2.8 and above @ is used to multiply matrices
        # using * still works but results in unexpected behaviour!
        obj.matrix_world = quat @ rollMatrix
        obj.location = loc

    point_at(camera, target_coord)

def _create_object(
    obj_type: str,
    name: None | str,
    location: tuple = (0,0,0),
    scale: tuple = (1,1,1),
    rotation: tuple = (0,0,0),
    collection: str = None,
) -> None:
    # Mapping of object creation methods
    obj_creators = {
        'cube': bpy.ops.mesh.primitive_cube_add,
        'sphere': bpy.ops.mesh.primitive_uv_sphere_add,
        'cylinder': bpy.ops.mesh.primitive_cylinder_add,
        'cone': bpy.ops.mesh.primitive_cone_add,
        'plane': bpy.ops.mesh.primitive_plane_add
    }

    if obj_type not in obj_creators:
        raise ValueError(f"Unsupported object obj_type: {obj_type}")

    # Create the object
    obj_creators[obj_type](
        location=location, 
        scale=scale
    )

    # Get the most recently created object
    obj = bpy.context.active_object
    obj.location = location
    
    # Set name if provided
    if name:
        obj.name = name

    # Set rotation
    obj.rotation_euler = rotation

    # Unlink from default collection and link to specified collection
    bpy.context.collection.objects.unlink(obj)
    
    if collection and collection in collections:
        collections[collection].objects.link(obj)
    else:
        bpy.context.collection.objects.link(obj)

def _create_collection(
    name: str,
    obj_types: list,
    obj_counts: list,
    placement: str,
    rand: str = None,
    lin_start_xyz: list = None,
    lin_distance: float = None,
    lin_axis: str = None,
    lin_noisy_offset: float = None,
    weights: list = None,
    sph_radius: float = None,
    sph_center: list = None,
    plane_corner1: list = None,
    plane_corner2: list = None,
    circle_radius: float = None,
    circle_center: list = None,
    circle_exclude_axis: str = None,
) -> None:
    obj_counts = [int(elem) for elem in obj_counts]
    collection = bpy.data.collections.new(name = name)
    bpy.context.scene.collection.children.link(collection)
    collections[name] = collection

    axis_to_idx = {
        'x': 0,
        'y': 1,
        'z': 2,
    }

    random_samplers = {
        "uniform": __uniform_sampler,
        "weighted": __weighted_sampler,
    }

    total_num_objs = np.sum(obj_counts)

    if "linear" in placement:
        obj_posns = np.ndarray((total_num_objs, 3))
        obj_posns[:] = lin_start_xyz
        obj_posns[:,axis_to_idx[lin_axis]] = np.arange(total_num_objs)*lin_distance
        
        if "gauss" in placement:
            obj_offsets_1 = np.random.normal(0, lin_noisy_offset, total_num_objs)
            obj_offsets_2 = np.random.normal(0, lin_noisy_offset, total_num_objs)
        else:
            obj_offsets_1 = np.zeros((total_num_objs,))
            obj_offsets_2 = np.zeros((total_num_objs,))
        
        idxs = []
        for axis in axis_to_idx:
            if axis != lin_axis:
                idxs.append(axis_to_idx[axis])
        
        obj_posns[:,  idxs[0]] += obj_offsets_1
        obj_posns[:,  idxs[1]] += obj_offsets_2
    elif "plane" in placement:
        diagonal_vec = (np.array(plane_corner2)-np.array(plane_corner1))
        obj_posns = np.ndarray((total_num_objs, 3))
        obj_posns[:] = np.array(plane_corner1) + diagonal_vec/2
        
        idxs = []
        for axis,i in enumerate(diagonal_vec):
            if not np.isclose(0.0, i):
                idxs.append(axis)

        obj_posns[:, idxs[0]] += np.random.uniform(-diagonal_vec[idxs[0]]/2, diagonal_vec[idxs[0]]/2, total_num_objs)
        obj_posns[:, idxs[1]] += np.random.uniform(-diagonal_vec[idxs[1]]/2, diagonal_vec[idxs[1]]/2, total_num_objs)
    elif "circle" in placement:
        r = circle_radius*np.sqrt(np.random.uniform(0, 1, size=total_num_objs))
        theta = np.random.uniform(0, 2 * np.pi, size=total_num_objs)

        idxs = []
        for axis in axis_to_idx:
            if axis != circle_exclude_axis:
                idxs.append(axis_to_idx[axis])

        obj_posns = np.ndarray((total_num_objs, 3))
        obj_posns[:] = circle_center
        obj_posns[:,  idxs[0]] += r * np.cos(theta)
        obj_posns[:,  idxs[1]] += r * np.sin(theta)
    elif "sphere" in placement:
        obj_posns = np.random.normal(size=(total_num_objs, 3))
        lambda_vals = (sph_radius*(np.random.uniform(0, 1, size=total_num_objs))**(1/3)) / np.sqrt(np.sum(obj_posns**2, axis=1))
        obj_posns = obj_posns * lambda_vals[:, np.newaxis]
        obj_posns[:] += sph_center
    else:
        raise NotImplementedError()

    if (len(obj_counts) != len(obj_types)):
        if len(obj_counts) != 1:
            raise ValueError
        if rand:
            for i in range(obj_counts[0]):
                _create_object(
                    obj_type=random_samplers[rand](obj_types, weights=weights),
                    name = None,
                    collection = name,
                    location=obj_posns[i],
                )
        else:
            for obj_type in obj_types:
                for i in range(obj_counts[0]):
                    _create_object(
                        obj_type=obj_type,
                        name=None,
                        collection = name,
                        location=obj_posns[i],
                    )
    else:
        for idx, (obj_type, cnt) in enumerate(zip(obj_types, obj_counts)):
            for i in range(cnt):
                _create_object(
                    obj_type=obj_type,
                    name=None,
                    collection = name,
                    location=obj_posns[np.sum(obj_counts[:idx], dtype=int).item()+i],
                )

def _create_light(
    name: str,
    type: str = 'POINT',
    location: tuple = (0,0,0),
    energy: float = 1000,
    color: tuple = (1,1,1),
    radius: float = 0.1,
    collection: str = None
) -> bpy.types.Object:
    """
    Create a light in Blender with customizable parameters.
    
    Parameters:
    - name: Name of the light object
    - type: Light type ('POINT', 'SUN', 'SPOT', 'AREA')
    - location: 3D coordinates of the light
    - energy: Light intensity
    - color: RGB color of the light (0-1 range)
    - radius: Radius for area lights
    - collection: Optional collection to link the light to
    
    Returns: Created light object
    """
    # List of valid light types
    valid_types = ['POINT', 'SUN', 'SPOT', 'AREA']
    
    # Validate light type
    if type.upper() not in valid_types:
        raise ValueError(f"Invalid light type. Choose from {valid_types}")
    
    # Create light data
    light_data = bpy.data.lights.new(name=name, type=type.upper())
    
    # Create light object
    light_object = bpy.data.objects.new(name=name, object_data=light_data)
    
    # Set light properties
    light_object.location = location
    light_data.energy = energy
    light_data.color = color
    # Set radius for area lights
    if type.upper() == 'AREA':
        light_data.size = radius
    
    if collection:
        if collection in bpy.data.collections:
            collections[collection].objects.link(light_object)
        else:
            raise ValueError(f"No collection found with name: {collection}")
    else:
        bpy.context.collection.objects.link(light_object)

def _hide_object(name: str, viewport: bool = True, render: bool = True) -> None:
    """
    Hide an object by name in viewport and/or render.
    
    Parameters:
    - name: Name of the object to hide
    - viewport: Whether to hide in viewport (default True)
    - render: Whether to hide in render (default True)
    """
    if name in bpy.data.objects:
        obj = bpy.data.objects[name]
        obj.hide_viewport = viewport
        obj.hide_render = render
    else:
        raise ValueError(f"Object '{name}' not found")

def _show_object(name: str, viewport: bool = True, render: bool = True) -> None:
    """
    Show an object by name in viewport and/or render.
    
    Parameters:
    - name: Name of the object to show
    - viewport: Whether to show in viewport (default True)
    - render: Whether to show in render (default True)
    """
    if name in bpy.data.objects:
        obj = bpy.data.objects[name]
        obj.hide_viewport = not viewport
        obj.hide_render = not render
    else:
        raise ValueError(f"Object '{name}' not found")

def _hide_collection(name: str, viewport: bool = True, render: bool = True) -> None:
    """
    Hide a collection by name in viewport and/or render.
    
    Parameters:
    - name: Name of the collection to hide
    - viewport: Whether to hide in viewport (default True)
    - render: Whether to hide in render (default True)
    """
    if name in bpy.data.collections:
        collection = bpy.data.collections[name]
        collection.hide_viewport = viewport
        collection.hide_render = render
        
        # Recursively hide all objects in the collection
        for obj in collection.objects:
            obj.hide_viewport = viewport
            obj.hide_render = render
    else:
        raise ValueError(f"Collection '{name}' not found")

def _show_collection(name: str, viewport: bool = True, render: bool = True) -> None:
    """
    Show a collection by name in viewport and/or render.
    
    Parameters:
    - name: Name of the collection to show
    - viewport: Whether to show in viewport (default True)
    - render: Whether to show in render (default True)
    """
    if name in bpy.data.collections:
        collection = bpy.data.collections[name]
        collection.hide_viewport = not viewport
        collection.hide_render = not render
        
        # Recursively show all objects in the collection
        for obj in collection.objects:
            obj.hide_viewport = not viewport
            obj.hide_render = not render
    else:
        raise ValueError(f"Collection '{name}' not found")

def _translate_object(name: str, 
                      translation: tuple = (0, 0, 0)):
    obj = bpy.data.objects.get(name)
    if not obj:
        raise ValueError(f"Object {name} not found")
    obj.location.x += translation[0]
    obj.location.y += translation[1]
    obj.location.z += translation[2]
        
def _rotate_object(name: str, 
                   rotation: tuple = (0, 0, 0)):
    obj = bpy.data.objects.get(name)
    if not obj:
        raise ValueError(f"Object {name} not found")
    obj.rotation_euler.x += rotation[0]
    obj.rotation_euler.y += rotation[1]
    obj.rotation_euler.z += rotation[2]

def _scale_object(name: str,
                  scale: tuple = (0, 0, 0)):
    obj = bpy.data.objects.get(name)
    if not obj:
        raise ValueError(f"Object {name} not found")
    obj.scale.x += scale[0]
    obj.scale.y += scale[1]
    obj.scale.z += scale[2]

def _translate_collection(name: str, 
                      translation: tuple = (0, 0, 0)):
    collection = bpy.data.collections[name]
    if not collection:
        raise ValueError(f"Collections {name} not found")
    for obj in collection.objects:
        obj.location.x += translation[0]
        obj.location.y += translation[1]
        obj.location.z += translation[2]
        
def _rotate_collection(name: str, 
                   rotation: tuple = (0, 0, 0)):
    collection = bpy.data.collections[name]
    if not collection:
        raise ValueError(f"Collections {name} not found")
    for obj in collection.objects:
        obj.rotation_euler.x += rotation[0]
        obj.rotation_euler.y += rotation[1]
        obj.rotation_euler.z += rotation[2]

def _scale_collection(name: str,
                  scale: tuple = (0, 0, 0)):
    collection = bpy.data.collections[name]
    if not collection:
        raise ValueError(f"Collections {name} not found")
    for obj in collection.objects:
        obj.scale.x += scale[0]
        obj.scale.y += scale[1]
        obj.scale.z += scale[2]

def _remove_random_faces_collection(
   name: str, 
   removal_fraction: float = 0.5, 
):
    collection = bpy.data.collections.get(name)
    for collection_obj in collection.all_objects:
        if collection_obj.type == 'MESH':
            __remove_faces_from_mesh(collection_obj, removal_fraction)

def _remove_random_faces_object(
    name: str,
    removal_fraction: float = 0.5,
):
    obj = bpy.data.objects.get(name)
    if obj and obj.type == 'MESH':
        __remove_faces_from_mesh(obj, removal_fraction)

def __remove_faces_from_mesh(mesh_obj, removal_fraction):
   """Internal function to remove faces from a single mesh object"""
   bpy.context.view_layer.objects.active = mesh_obj
   bpy.ops.object.mode_set(mode='EDIT')
   bpy.ops.mesh.select_mode(type='FACE')
   
   # Select mesh
   bpy.ops.mesh.select_all(action='SELECT')
   mesh = mesh_obj.data
   # Get total face count
   total_faces = len(mesh_obj.data.polygons)
   faces_to_remove = int(total_faces * removal_fraction)

   face_indices = list(range(len(mesh.polygons)))

   # Randomly select faces to remove
   selected_faces = random.sample(face_indices, faces_to_remove)

    # Enter edit mode
   bpy.ops.object.mode_set(mode='EDIT')
   bpy.ops.mesh.select_mode(type='FACE')
   bpy.ops.mesh.select_all(action='DESELECT')

    # Select the chosen faces
   bpy.ops.object.mode_set(mode='OBJECT')
   for face_index in selected_faces:
       mesh.polygons[face_index].select = True

    # Switch back to edit mode and delete selected faces
   bpy.ops.object.mode_set(mode='EDIT')
   bpy.ops.mesh.delete(type='FACE')

    # Return to object mode
   bpy.ops.object.mode_set(mode='OBJECT')


def _save_scene(name: str):
    bpy.ops.wm.save_mainfile(filepath=f"{name}.blend")
    
# _create_collection(
#     "hi",
#     ["cube", "sphere", "cylinder"],
#     [5,3,4],
#     rand=None,
#     placement="sphere",
#     start_xyz=[0,0,20],
#     sph_radius=10.0,
# )

# Linear
# placement="linear",
# start_xyz=(5,5,5),
# lin_distance=5.0,
# lin_axis="x",

# Linear Gauss
# placement="linear_gauss",
# start_xyz=(5,5,5),
# lin_distance=5.0,
# lin_axis="x",
# lin_noisy_offset=4.0

# Plane
# placement="plane",
# plane_corner1=[-10,-10,0],
# plane_corner2=[10,10,0]

# Circle
# placement="circle",
# start_xyz=[0,0,10],
# circle_exclude_axis="z",
# circle_radius=10.0,

# Sphere
# placement="sphere",
# start_xyz=[0,0,20],
# sph_radius=10.0,

# _create_light(
#     name="White",
#     location=[5,3,10],
# )

# _create_light(
#     name="Red",
#     location=[5,3,20],
#     collection="hi",
#     type='AREA',
#     color=(1, 0, 0),
# )

# _create_camera(
#     name="Cacm",
#     target_collection="hi",
#     r=30,
#     theta=0,
#     phi=0,
# )

# _create_object(
#     "cube",
#     name="hi"
# )

# hide_collection("hi")

# bpy.ops.wm.save_mainfile(filepath="./sphere.blend")