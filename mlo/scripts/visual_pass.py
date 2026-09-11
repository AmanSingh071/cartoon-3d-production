import bpy, os, json, math
from mathutils import Vector

ROOT = r'D:\first Blender\mlo'
OUT = os.path.join(ROOT, 'output')
BLEND = os.path.join(OUT, 'Nocturne_Lounge_MLO.blend')
PREVIEW = os.path.join(OUT, 'mlo_showcase.png')
MANIFEST = os.path.join(OUT, 'mlo_manifest.json')

if not os.path.exists(BLEND):
    raise RuntimeError('visual_pass: missing base blend')

bpy.ops.wm.open_mainfile(filepath=BLEND)

# ---------- shared materials ----------
def material(name, base, metallic=0.0, rough=0.5, emission=None, strength=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*base, 1)
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = rough
    if emission is not None:
        if 'Emission Color' in bs.inputs: bs.inputs['Emission Color'].default_value = (*emission, 1)
        if 'Emission Strength' in bs.inputs: bs.inputs['Emission Strength'].default_value = strength
    return m

floor = material('VIS_Floor', (0.025,0.035,0.05), 0.35, 0.24)
wall = material('VIS_Wall', (0.07,0.065,0.075), 0.05, 0.58)
wood = material('VIS_Walnut', (0.12,0.035,0.015), 0.08, 0.28)
leather = material('VIS_Leather', (0.055,0.012,0.018), 0.0, 0.32)
fabric = material('VIS_Fabric', (0.018,0.022,0.032), 0.0, 0.78)
metal = material('VIS_Metal', (0.16,0.18,0.21), 0.82, 0.2)
gold = material('VIS_Gold', (0.42,0.16,0.025), 0.92, 0.14)
glass = material('VIS_Glass', (0.015,0.07,0.09), 0.65, 0.08)
cyan = material('VIS_Cyan', (0.002,0.05,0.08), 0.0, 0.2, (0.0,0.75,1.0), 7.0)
magenta = material('VIS_Magenta', (0.06,0.002,0.035), 0.0, 0.2, (1.0,0.01,0.35), 7.0)
amber = material('VIS_Amber', (0.08,0.025,0.002), 0.0, 0.22, (1.0,0.16,0.015), 5.0)
green = material('VIS_Green', (0.012,0.075,0.025), 0.0, 0.72)

# Map the original material names to the richer visual library.
replacements = {
    'Floor_DarkStone': floor, 'Wall_WarmConcrete': wall, 'Trim_BrushedMetal': metal,
    'Wood_Walnut': wood, 'Leather_DeepBrown': leather, 'Fabric_Charcoal': fabric,
    'Glass_Tinted': glass, 'Gold': gold, 'Neon_Cyan': cyan,
    'Neon_Magenta': magenta, 'Neon_Amber': amber, 'Plant_Green': green,
}
for obj in bpy.data.objects:
    if obj.type != 'MESH': continue
    for i, slot in enumerate(obj.material_slots):
        if slot.material and slot.material.name in replacements:
            obj.data.materials[i] = replacements[slot.material.name]

# ---------- visual architecture accents ----------
def cube(name, loc, scale, mat, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if bevel:
        b=o.modifiers.new('VisualBevel','BEVEL'); b.width=bevel; b.segments=2
    return o

def cyl(name, loc, radius, depth, mat, verts=16):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth, location=loc)
    o=bpy.context.object; o.name=name; o.data.materials.append(mat); return o

# recessed wall strips and floor perimeter glow: low-poly emissive geometry, not extra lights
for x in (-12.7, 12.7):
    cube('VIS_WallGlow', (x,0,1.35), (0.025,8.8,0.035), cyan, 0.008)
for y in (-9.7, 9.65):
    cube('VIS_PerimeterGlow', (0,y,0.22), (10.5,0.025,0.025), magenta if y < 0 else cyan, 0.006)

# Bar underglow and back-bar highlights
cube('VIS_BarUnderGlow', (8.3,-0.36,0.35), (3.75,0.035,0.035), amber, 0.006)
for x in (8.0,9.2,10.4,11.4):
    cube('VIS_BarShelfGlow', (x,1.83,1.02), (0.035,0.75,0.018), amber, 0.004)

# Stage edge and DJ canopy accents
cube('VIS_StageGlow', (0,5.25,0.48), (5.0,0.035,0.045), cyan, 0.008)
for x in (-4.4,-2.2,0,2.2,4.4):
    cube('VIS_DanceGrid', (x,1.8,0.215), (0.018,2.75,0.012), cyan, 0.004)

# ---------- lighting ----------
for obj in list(bpy.data.objects):
    if obj.type == 'LIGHT' and obj.name.startswith('VIS_'):
        bpy.data.objects.remove(obj, do_unlink=True)

def look_at(obj, target):
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()

def area(name, loc, target, energy, size, color):
    bpy.ops.object.light_add(type='AREA', location=loc)
    l=bpy.context.object; l.name=name; l.data.energy=energy; l.data.shape='DISK'; l.data.size=size; l.data.color=color; look_at(l,target); return l

def spot(name, loc, target, energy, size, blend, color):
    bpy.ops.object.light_add(type='SPOT', location=loc)
    l=bpy.context.object; l.name=name; l.data.energy=energy; l.data.color=color; l.data.spot_size=size; l.data.spot_blend=blend; l.data.shadow_soft_size=0.35; look_at(l,target); return l

# Eight purposeful lights cover the key zones instead of dozens of dynamic lights.
area('VIS_Bar_Key',(8,-1.5,3.8),(8,0.4,1.1),420,3.2,(1.0,0.34,0.10))
area('VIS_VIP_Key',(-6,4.8,3.6),(-6,5.0,0.8),360,3.5,(0.32,0.48,1.0))
area('VIS_Dining_Key',(0,-3.0,3.7),(0,-3.2,0.5),320,4.0,(1.0,0.58,0.32))
area('VIS_Entrance_Key',(0,-8.5,3.6),(0,-5.0,1.0),300,3.0,(0.30,0.70,1.0))
spot('VIS_Stage_Cyan',(-4.2,4.0,3.7),(0,7.0,1.0),700,0.72,0.42,(0.0,0.70,1.0))
spot('VIS_Stage_Magenta',(4.2,4.0,3.7),(0,7.0,1.0),700,0.72,0.42,(1.0,0.02,0.35))
spot('VIS_Back_Wash',(0,8.2,3.7),(0,9.7,1.8),420,0.9,0.55,(0.45,0.10,1.0))
spot('VIS_Floor_Wash',(0,-1.5,3.9),(0,0,0),260,1.15,0.65,(0.10,0.55,1.0))

# World remains dark so the accent palette reads clearly.
world=bpy.context.scene.world
world.use_nodes=True
bg=world.node_tree.nodes.get('Background')
if bg:
    bg.inputs['Color'].default_value=(0.003,0.004,0.008,1)
    bg.inputs['Strength'].default_value=0.16

scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=1920; scene.render.resolution_y=1080; scene.render.resolution_percentage=70
scene.render.image_settings.file_format='PNG'
scene.render.filepath=PREVIEW
try: scene.view_settings.look='AgX - Medium High Contrast'
except Exception: pass
scene['mlo_visual_pass']='color_lighting_v1'
scene['mlo_visual_lighting_count']=8
scene['mlo_visual_palette']='dark luxury / cyan / magenta / amber'
scene['mlo_visual_optimization']='8 purposeful lights + emissive accent geometry; shared materials'

bpy.ops.wm.save_as_mainfile(filepath=BLEND)
bpy.ops.render.render(write_still=True)

meta={}
if os.path.exists(MANIFEST):
    try:
        with open(MANIFEST,'r',encoding='utf-8') as f: meta=json.load(f)
    except Exception: pass
meta['latest_pass']='color_lighting_v1'
meta['status']='visual pass complete - architecture preserved'
meta['lighting']={'purposeful_lights':8,'palette':'cyan/magenta/amber','dynamic_light_budget':'controlled'}
with open(MANIFEST,'w',encoding='utf-8') as f: json.dump(meta,f,indent=2)
print('VISUAL PASS COMPLETE:', BLEND)
