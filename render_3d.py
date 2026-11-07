
import bpy
import math
import os
from mathutils import Vector

# Save video directly inside GitHub repository workspace
WORKSPACE = os.environ.get("GITHUB_WORKSPACE", os.getcwd())
os.chdir(WORKSPACE)
OUTPUT = os.path.join(WORKSPACE, "short.mp4")

# Reset Blender
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

scene = bpy.context.scene

# Render settings
scene.render.engine = "BLENDER_EEVEE_NEXT"
scene.render.resolution_x = 720
scene.render.resolution_y = 1280
scene.render.resolution_percentage = 100
scene.render.fps = 24
scene.frame_start = 1
scene.frame_end = 240

scene.render.image_settings.file_format = "FFMPEG"
scene.render.ffmpeg.format = "MPEG4"
scene.render.ffmpeg.codec = "H264"
scene.render.filepath = OUTPUT

# Color management
scene.view_settings.view_transform = "Standard"

# Materials
def material(name, color, metallic=0.0, roughness=0.5):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return mat

blue = material("Noob Blue", (0.025, 0.25, 0.95), 0.1)
yellow = material("Noob Yellow", (1.0, 0.68, 0.02))
white = material("Eye White", (1, 1, 1))
black = material("Black", (0.005, 0.005, 0.01))
green = material("Neon Green", (0.02, 0.8, 0.15), 0.2)
red = material("Hot Lava", (1, 0.035, 0.005), 0.1)
dark = material("Dark Background", (0.008, 0.012, 0.035))
orange = material("Orange Glow", (1, 0.22, 0.005), 0.1)

def cube(name, location, scale, mat, bevel=0.08):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)

    if bevel:
        mod = obj.modifiers.new("Smooth Edges", "BEVEL")
        mod.width = bevel
        mod.segments = 3
        obj.modifiers.new("Weighted Normals", "WEIGHTED_NORMAL")

    return obj

def animate_location(obj, frames):
    for frame, location in frames:
        obj.location = location
        obj.keyframe_insert(data_path="location", frame=frame)

def aim(obj, point):
    obj.rotation_euler = (Vector(point) - obj.location).to_track_quat("-Z", "Y").to_euler()

# Background and floor
cube("World Floor", (0, 0, -1.0), (18, 8, 1), dark, 0.1)

# Obby platforms
platforms = [
    (-3.0, 0, 0.2),
    (-1.5, 0, 1.0),
    (0.0, 0, 1.8),
    (1.5, 0, 2.6),
    (3.0, 0, 3.4),
]

for i, pos in enumerate(platforms):
    cube(
        "Obby Platform " + str(i),
        pos,
        (1.35, 2.0, 0.3),
        green,
        0.12
    )

# Lava
lava = cube("Rising Lava", (0, 1, -1.7), (12, 5, 1.2), red, 0.15)

animate_location(lava, [
    (1, (0, 1, -1.7)),
    (120, (0, 1, 0.0)),
    (240, (0, 1, 2.0))
])

# Lava glow blocks
for i in range(8):
    x = -3.5 + i
    cube(
        "Lava Glow " + str(i),
        (x, -1.4, -0.7),
        (0.35, 0.15, 0.25),
        orange,
        0.05
    )

# Noob character root
bpy.ops.object.empty_add(type="PLAIN_AXES", location=(-3, -0.2, 0.9))
root = bpy.context.object
root.name = "Noob Character"

def character_part(name, location, scale, mat):
    obj = cube(name, location, scale, mat)
    obj.parent = root
    return obj

# Body
character_part("Blue Body", (0, 0, 0.65), (0.85, 0.5, 1.0), blue)

# Head
character_part("Yellow Head", (0, 0, 1.55), (0.9, 0.75, 0.8), yellow)

# Eyes
character_part("Left Eye", (-0.2, -0.385, 1.65), (0.13, 0.06, 0.16), white)
character_part("Right Eye", (0.2, -0.385, 1.65), (0.13, 0.06, 0.16), white)

# Smile
character_part("Smile", (0, -0.4, 1.39), (0.3, 0.06, 0.07), black)

# Arms and legs
left_arm = character_part("Left Arm", (-0.57, 0, 0.75), (0.28, 0.35, 0.95), yellow)
right_arm = character_part("Right Arm", (0.57, 0, 0.75), (0.28, 0.35, 0.95), yellow)
left_leg = character_part("Left Leg", (-0.23, 0, -0.05), (0.3, 0.4, 0.65), blue)
right_leg = character_part("Right Leg", (0.23, 0, -0.05), (0.3, 0.4, 0.65), blue)

# Character jumps across the obby
animate_location(root, [
    (1, (-3, -0.2, 0.9)),
    (45, (-1.5, -0.2, 2.0)),
    (85, (-1.5, -0.2, 1.9)),
    (125, (0.0, -0.2, 2.8)),
    (165, (1.5, -0.2, 3.6)),
    (205, (3.0, -0.2, 4.4)),
    (240, (3.0, -0.2, 4.4))
])

# Arm movement
for frame, angle in [(1, 0), (45, 0.7), (85, -0.4),
                     (125, 0.8), (165, -0.3), (205, 0.7), (240, 0)]:
    left_arm.rotation_euler[1] = angle
    left_arm.keyframe_insert(data_path="rotation_euler", frame=frame)
    right_arm.rotation_euler[1] = -angle
    right_arm.keyframe_insert(data_path="rotation_euler", frame=frame)

# 3D title
def add_text(body, location, size, mat):
    bpy.ops.object.text_add(location=location)
    obj = bpy.context.object
    obj.data.body = body
    obj.data.size = size
    obj.data.extrude = 0.025
    obj.data.materials.append(mat)
    obj.rotation_euler[0] = math.radians(90)
    return obj

title = add_text("NOOB VS LAVA!", (0, -2.8, 8.0), 0.8, yellow)
title.keyframe_insert(data_path="scale", frame=1)
title.scale = (1.15, 1.15, 1.15)
title.keyframe_insert(data_path="scale", frame=20)

hook = add_text("CAN HE ESCAPE?", (0, -2.8, 7.0), 0.42, white)

# Camera
bpy.ops.object.camera_add(location=(0, -23, 8))
camera = bpy.context.object
aim(camera, (0, 0, 3.5))
camera.data.lens = 48
scene.camera = camera

# Lighting
def area_light(name, location, power, color, size):
    bpy.ops.object.light_add(type="AREA", location=location)
    light = bpy.context.object
    light.name = name
    light.data.energy = power
    light.data.color = color
    light.data.shape = "DISK"
    light.data.size = size
    aim(light, (0, 0, 2))
    return light

area_light("Main Light", (0, -8, 10), 1800, (0.7, 0.85, 1.0), 8)
area_light("Warm Lava Light", (0, 3, 2), 1200, (1.0, 0.12, 0.02), 6)
area_light("Top Light", (3, 2, 10), 1500, (0.1, 0.5, 1.0), 5)

# World background
world = bpy.data.worlds.new("SharkX World") if not bpy.data.worlds else bpy.data.worlds[0]
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.008, 0.012, 0.035, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.35

# Render quality
scene.render.resolution_percentage = 100
scene.render.image_settings.color_mode = "RGB"
scene.render.ffmpeg.constant_rate_factor = "MEDIUM"
scene.render.ffmpeg.ffmpeg_preset = "GOOD"

# Ensure output path is absolute
scene.render.filepath = OUTPUT

# Render animation
scene.frame_set(1)
bpy.ops.render.render(animation=True)

# Confirm output exists
if not os.path.isfile(OUTPUT) or os.path.getsize(OUTPUT) == 0:
    raise RuntimeError("Render finished but short.mp4 was not created: " + OUTPUT)

print("SUCCESS: Video created at " + OUTPUT)
   
