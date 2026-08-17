import bpy
import math
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUTPUT = os.path.join(ROOT, "public", "models", "son_of_god_cap.glb")

bpy.ops.wm.read_factory_settings(use_empty=True)

def material(name, color, roughness=0.6):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Roughness"].default_value = roughness
    return mat

cloth = material("SOG_Cloth", (0.10, 0.11, 0.14), 0.78)
trim = material("SOG_Trim", (0.035, 0.04, 0.055), 0.5)
embroidery = material("SOG_Embroidery", (0.72, 0.77, 0.88), 0.34)

# Crown: an open, proportioned six-panel dome (not a full sphere).
segments, rings = 64, 18
vertices = [(0, 0, 0.93)]
for ring in range(1, rings + 1):
    phi = (math.pi / 2) * ring / rings
    for segment in range(segments):
        theta = 2 * math.pi * segment / segments
        vertices.append((0.84 * math.sin(phi) * math.cos(theta), 0.72 * math.sin(phi) * math.sin(theta), 0.12 + 0.81 * math.cos(phi)))
faces = []
for segment in range(segments):
    faces.append((0, 1 + segment, 1 + (segment + 1) % segments))
for ring in range(1, rings):
    row = 1 + (ring - 1) * segments
    next_row = row + segments
    for segment in range(segments):
        nxt = (segment + 1) % segments
        faces.append((row + segment, next_row + segment, next_row + nxt, row + nxt))
mesh = bpy.data.meshes.new("SOG_Crown")
mesh.from_pydata(vertices, [], faces)
mesh.materials.append(cloth)
crown = bpy.data.objects.new("SOG_Crown", mesh)
bpy.context.collection.objects.link(crown)
for polygon in mesh.polygons:
    polygon.use_smooth = True

# Curved visor: an oval disk whose rear half tucks under the crown.
visor_vertices = [(0, -0.56, 0.18)]
visor_faces = []
for index in range(48):
    angle = 2 * math.pi * index / 48
    x = 0.96 * math.cos(angle)
    y = -0.56 + 0.62 * math.sin(angle)
    z = 0.16 + 0.10 * (x / 0.96) ** 2 - 0.055 * max(0, -math.sin(angle))
    visor_vertices.append((x, y, z))
for index in range(48):
    visor_faces.append((0, 1 + index, 1 + (index + 1) % 48))
visor_mesh = bpy.data.meshes.new("SOG_Visor")
visor_mesh.from_pydata(visor_vertices, [], visor_faces)
visor_mesh.materials.append(cloth)
visor = bpy.data.objects.new("SOG_Visor", visor_mesh)
bpy.context.collection.objects.link(visor)
for polygon in visor_mesh.polygons:
    polygon.use_smooth = True
solid = visor.modifiers.new("Visor thickness", "SOLIDIFY")
solid.thickness = 0.045
solid.offset = -1
bevel = visor.modifiers.new("Visor soft edge", "BEVEL")
bevel.width = 0.018
bevel.segments = 3

def curve_object(name, points, radius, mat):
    data = bpy.data.curves.new(name, "CURVE")
    data.dimensions = "3D"
    data.resolution_u = 16
    data.bevel_depth = radius
    data.bevel_resolution = 3
    spline = data.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    for node, point in zip(spline.bezier_points, points):
        node.co = point
        node.handle_left_type = "AUTO"
        node.handle_right_type = "AUTO"
    data.materials.append(mat)
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    return obj

# Six panel seams closely follow the dome, plus the lower piping.
for index in range(6):
    theta = 2 * math.pi * index / 6
    points = []
    for step in range(7):
        phi = (math.pi / 2) * step / 6
        points.append((0.846 * math.sin(phi) * math.cos(theta), 0.726 * math.sin(phi) * math.sin(theta), 0.12 + 0.816 * math.cos(phi)))
    curve_object(f"SOG_Panel_Seam_{index}", points, 0.006, trim)
curve_object("SOG_Lower_Piping", [(0.84 * math.cos(i * 2 * math.pi / 32), 0.72 * math.sin(i * 2 * math.pi / 32), 0.125) for i in range(33)], 0.009, trim)

# Embroidered SOG mark on the front crown. It uses the same local surface as
# the product, and is exported in the GLB as a permanent material/mesh.
front_y = -0.709
curve_object("SOG_Embroidery_A", [(-0.16, front_y, 0.43), (-0.08, front_y - 0.01, 0.47), (-0.01, front_y - 0.025, 0.56), (0.06, front_y - 0.04, 0.67)], 0.017, embroidery)
curve_object("SOG_Embroidery_B", [(-0.09, front_y - 0.008, 0.34), (-0.01, front_y - 0.024, 0.39), (0.06, front_y - 0.04, 0.48), (0.13, front_y - 0.055, 0.57)], 0.017, embroidery)

# Crown button.
bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=10, location=(0, 0, 0.935), scale=(0.07, 0.07, 0.04))
button = bpy.context.object
button.name = "SOG_Top_Button"
button.data.materials.append(trim)

# Convert curves so the GLB has no procedural dependencies.
for obj in list(bpy.context.scene.objects):
    if obj.type == "CURVE":
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.convert(target="MESH")
        obj.select_set(False)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.gltf(filepath=OUTPUT, export_format="GLB", export_materials="EXPORT", export_cameras=False, export_lights=False)
