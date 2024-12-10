let center_pt [0,0,20]

create collection (
    name = "spheres",
    obj_types = ["sphere"],
    obj_counts = [10],
    placement = "sphere",
    sph_center = center_pt,
    sph_radius = 10.0
)

create object (
    name = "bigsphere",
    obj_type = "sphere",
    location = center_pt,
    scale = [10,10,10]
)

operation remove_faces (
    op_target = "object",
    name = "bigsphere",
    removal_fraction = 0.5
)

create light (
    name = "White",
    location = center_pt
)

create camera (
    name = "Cam",
    target_coord = center_pt,
    r = 50,
    theta = 45,
    phi = 45
)

save ("test_scene")