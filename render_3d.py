
import bpy
import math
from mathutils import Vector

# Reset scene
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE_NEXT"
scene.render.resolution_x = 720
scene.render.resolution_y = 1280
scene.render.resolution_percentage = 100
scene.render.fps = 24
scene.frame_start = 1
scene.frame_end = 432

# Materials
def material(name, color, metallic=0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    bs = mat.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*color, 1)
    bs.inputs["Metallic"].default_value = metallic
    return mat

blue = material("Noob Blue", (0.03, 0.25, 0.95))
yellow = material("Noob Head", (1.0, 0.65, 0.03))
white = material("Eyes", (1, 1, 1))
black = material("Black", (0.015, 0.015, 0.025))
green = material("Platforms", (0.03, 0.65, 0.22))
red = material("Rising Lava", (1, 0.035, 0.005), 0.2)
dark = material("Environment", (0.025, 0.04, 0.11))

def cube(name, location, scale, mat, bevel=0.08):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)

    if bevel:
        mod = obj.modifiers.new("Smooth edges", "BEVEL")
        mod.width = bevel
        mod.segments = 3
        obj.modifiers.new("Weighted normals", "WEIGHTED_NORMAL")

    return obj

# Environment
cube("Ground", (0, 0, -0.5), (18, 18, 1), dark, 0.1)

for i in range(7):
    x = -3 + i * 1.1
    z = 0.4 + (i % 2) * 0.35
    cube("Escape platform", (x, 0, z), (1.5, 2.2, 0.35), green)

# Lava
lava = cube("Rising lava", (0, 2, -1.0), (18, 12, 1), red, 0.15)
lava.keyframe_insert(data_path="location", frame=1)
lava.location.z = 1.8
lava.keyframe_insert(data_path="location", frame=432)

# Character root
root = bpy.data.objects.new("NOOB Character", None)
scene.collection.objects.link(root)

def part(name, loc, scale, mat):
    obj = cube(name, loc, scale, mat, 0.06)
    obj.parent = root
    obj.location = loc
    return obj

# Body
part("Blue body", (0, 0, 1.5), (0.8, 0.45, 1.0), blue)
part("Yellow head", (0, 0, 2.35), (0.75, 0.65, 0.7), yellow)

# Face
part("Left eye", (-0.17, -0.34, 2.43), (0.12, 0.06, 0.13), black)
part("Right eye", (0.17, -0.34, 2.43), (0.12, 0.06, 0.13), black)
part("Smile", (0, -0.35, 2.18), (0.22, 0.05, 0.06), black)

# Arms and legs
left_arm = part("Left arm", (-0.55, 0, 1.55), (0.28, 0.35, 0.85), yellow)
right_arm = part("Right arm", (0.55, 0, 1.55), (0.28, 0.35, 0.85), yellow)
left_leg = part("Left leg", (-0.22, 0, 0.75), (0.3, 0.4, 0.7), blue)
right_leg = part("Right leg", (0.22, 0, 0.75), (0.3, 0.4, 0.7), blue)

# Character movement
for frame, x, z in [
    (1, -3, 0),
    (90, -1.5, 0),
    (135, -0.8, 1.5),
    (180, 0, 0),
    (250, 1.5, 1.4),
    (310, 2.3, 0),
    (432, 3.0, 0)
]:
    root.location = (x, 0, z)
    root.keyframe_insert(data_path="location", frame=frame)

# Animate arms
for frame, angle in [(1, 0), (90, 0.5), (135, -0.8),
                     (180, 0.6), (250, -0.8), (432, 0)]:
    left_arm.rotation_euler[1] = angle
    left_arm.keyframe_insert(data_path="rotation_euler", frame=frame)
    right_arm.rotation_euler[1] = -angle
    right_arm.keyframe_insert(data_path="rotation_euler", frame=frame)

# Camera
bpy.ops.object.camera_add(location=(8, -17, 11))
camera = bpy.context.object
camera.rotation_euler = (Vector((0, 0, 2)) - camera.location).to_track_quat("-Z", "Y").to_euler()
camera.data.lens = 48
scene.camera = camera

# Lighting
bpy.ops.object.light_add(type="AREA", location=(0, -8, 12))
light = bpy.context.object
light.data.energy = 1800
light.data.shape = "DISK"
light.data.size = 9
light.rotation_euler = (Vector((0, 0, 1)) - light.location).to_track_quat("-Z", "Y").to_euler()

# Story title
bpy.ops.object.text_add(location=(0, -4, 7))
title = bpy.context.object
title.data.body = "NOOB VS RISING LAVA!"
title.data.align_x = "CENTER"
title.data.size = 0.65
title.data.extrude = 0.015
title.rotation_euler = (math.radians(90), 0, 0)
title.data.materials.append(yellow)

# World and render
scene.world.color = (0.025, 0.025, 0.06)
scene.render.image_settings.file_format = "FFMPEG"
scene.render.ffmpeg.format = "MPEG4"
scene.render.ffmpeg.codec = "H264"
scene.render.filepath = "short.mp4"
scene.render.image_settings.color_mode = "RGB"

# Render
bpy.ops.render.render(animation=True)
