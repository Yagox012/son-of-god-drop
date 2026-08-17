import bpy
import math
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SOURCE = os.path.join(ROOT, "public", "models", "baseball_cap.glb")
OUTPUT = os.path.join(ROOT, "public", "models", "inspection")

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SOURCE)

for obj in bpy.context.scene.objects:
    if obj.type == "MESH":
        for material in obj.data.materials:
            if material:
                material.diffuse_color = (0.12, 0.13, 0.16, 1)

world = bpy.data.worlds.new("World")
world.color = (0.012, 0.014, 0.02)
bpy.context.scene.world = world

def add_light(location, energy, size, color):
    data = bpy.data.lights.new("Studio", "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    data.color = color
    light = bpy.data.objects.new("Studio", data)
    bpy.context.collection.objects.link(light)
    light.location = location
    return light

def point_at(obj, target=(0, 0, 0)):
    obj.rotation_euler = (mathutils.Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()

import mathutils
add_light((4, 5, 4), 900, 4, (0.86, 0.90, 1.0))
add_light((-4, 2, 3), 650, 3, (1.0, 0.74, 0.62))

camera_data = bpy.data.cameras.new("Camera")
camera_data.lens = 52
camera = bpy.data.objects.new("Camera", camera_data)
bpy.context.collection.objects.link(camera)
bpy.context.scene.camera = camera

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 720
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False

os.makedirs(OUTPUT, exist_ok=True)
for label, location in {
    "plus_z": (0, 0.025, 0.48),
    "minus_z": (0, 0.025, -0.48),
    "plus_x": (0.48, 0.025, 0),
    "minus_x": (-0.48, 0.025, 0),
    "plus_y": (0, 0.48, 0.025),
    "minus_y": (0, -0.48, 0.025),
}.items():
    camera.location = location
    point_at(camera)
    scene.render.filepath = os.path.join(OUTPUT, f"{label}.png")
    bpy.ops.render.render(write_still=True)
