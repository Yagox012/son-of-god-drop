import bpy
import math
import os

SOURCE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "public", "models", "baseball_cap.glb"))
OUTPUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "public", "models", "son_of_god_cap.glb"))

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SOURCE)

cap_meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
if not cap_meshes:
    raise RuntimeError("No cap meshes found")

# Make one independent projection surface without touching the imported cap.
vertices = []
faces = []
for obj in cap_meshes:
    base_index = len(vertices)
    vertices.extend([obj.matrix_world @ vertex.co for vertex in obj.data.vertices])
    faces.extend([[base_index + index for index in polygon.vertices] for polygon in obj.data.polygons])
target_mesh = bpy.data.meshes.new("SOG_Shrinkwrap_Surface")
target_mesh.from_pydata(vertices, [], faces)
target_mesh.update()
target = bpy.data.objects.new("SOG_Shrinkwrap_Target", target_mesh)
bpy.context.collection.objects.link(target)
target.name = "SOG_Shrinkwrap_Target"
target.hide_render = True
target.hide_viewport = True

embroidery = bpy.data.materials.new("SOG_Embroidery")
embroidery.diffuse_color = (0.05, 0.06, 0.08, 1)
embroidery.use_nodes = True
bsdf = embroidery.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.05, 0.06, 0.08, 1)
bsdf.inputs["Roughness"].default_value = 0.38

def make_thread(name, points):
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 24
    # El modelo fuente es amplio; el primer bordado quedó demasiado pequeño
    # para leerse desde la cámara de la landing. Este grosor deja un relieve
    # discreto pero claramente visible, como una pieza de silicón/embroidery.
    curve.bevel_depth = 0.0038
    curve.bevel_resolution = 4
    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    for point, co in zip(spline.bezier_points, points):
        point.co = co
        point.handle_left_type = "AUTO"
        point.handle_right_type = "AUTO"
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(embroidery)
    shrink = obj.modifiers.new("Conform_to_cap", "SHRINKWRAP")
    shrink.target = target
    shrink.wrap_method = "PROJECT"
    shrink.use_project_y = True
    shrink.use_negative_direction = True
    shrink.wrap_mode = "ON_SURFACE"
    shrink.offset = 0.0012
    return obj

# This is the two-stroke SOG glyph from the approved reference. Coordinates
# sit on the front crown; shrinkwrap makes the threads follow the exact fabric.
# The negative-Z projection lands on the rear strap; the product mark belongs
# only on the front crown, so we export the front pair below.
make_thread("SOG_Thread_Front_A", [(-0.040, 0.24, 0.018), (-0.014, 0.24, 0.029), (0.008, 0.24, 0.049), (0.030, 0.24, 0.074)])
make_thread("SOG_Thread_Front_B", [(-0.021, 0.24, -0.014), (0.005, 0.24, -0.001), (0.028, 0.24, 0.019), (0.048, 0.24, 0.044)])

# Apply the projection so the exported GLB is self-contained.
for obj in [o for o in bpy.context.scene.objects if o.name.startswith("SOG_Thread")]:
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target="MESH")
    obj.select_set(False)

bpy.data.objects.remove(target, do_unlink=True)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.gltf(filepath=OUTPUT, export_format="GLB", export_materials="EXPORT", export_cameras=False, export_lights=False)
