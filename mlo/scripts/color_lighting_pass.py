import bpy, math, os
from mathutils import Vector

ROOT = r'D:\first Blender\mlo'
OUT = os.path.join(ROOT, 'output')
BLEND = os.path.join(OUT, 'Nocturne_Lounge_MLO.blend')

# CRITICAL: this is a post-build pass. Always open the generated lounge first.
if not os.path.exists(BLEND):
    raise RuntimeError('color_lighting_pass: missing generated MLO')
bpy.ops.wm.open_mainfile(filepath=BLEND)

# ---------- material polish ----------
def set_principled(name, base, metallic, rough, emission=None, strength=0.0):
    m = bpy.data.materials.get(name)
    if not m or not m.use_nodes:
        return
    bs = m.node_tree.nodes.get('Principled BSDF')
    if not bs:
        return
    bs.inputs['Base Color'].default_value = (*base, 1)
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = rough
    if emission:
        if 'Emission Color' in bs.inputs: bs.inputs['Emission Color'].default_value = (*emission, 1)
        if 'Emission Strength' in bs.inputs: bs.inputs['Emission Strength'].default_value = strength

set_principled('Floor_DarkStone',(0.018,0.024,0.032),0.35,0.20)
set_principled('Wall_WarmConcrete',(0.075,0.065,0.060),0.0,0.55)
set_principled('Trim_BrushedMetal',(0.16,0.18,0.20),0.82,0.18)
set_principled('Wood_Walnut',(0.22,0.055,0.018),0.08,0.28)
set_principled('Leather_DeepBrown',(0.055,0.012,0.008),0.0,0.25)
set_principled('Fabric_Charcoal',(0.018,0.022,0.028),0.0,0.78)
set_principled('Glass_Tinted',(0.012,0.055,0.075),0.65,0.07)
set_principled('Gold',(0.62,0.20,0.025),0.92,0.13)
set_principled('Plant_Green',(0.012,0.085,0.022),0.0,0.62)
set_principled('Display_White',(0.65,0.70,0.78),0.05,0.24)
set_principled('Neon_Cyan',(0.005,0.06,0.08),0.0,0.24,(0.0,0.75,1.0),12)
set_principled('Neon_Magenta',(0.07,0.005,0.045),0.0,0.24,(1.0,0.01,0.34),10)
set_principled('Neon_Amber',(0.10,0.025,0.002),0.0,0.24,(1.0,0.12,0.01),8)

# Replace old generated lights only; preserve all geometry.
for obj in list(bpy.data.objects):
    if obj.type == 'LIGHT':
        bpy.data.objects.remove(obj, do_unlink=True)

def area(name, loc, color, energy, size, target):
    bpy.ops.object.light_add(type='AREA', location=loc)
    l=bpy.context.object; l.name=name; l.data.energy=energy; l.data.color=color; l.data.shape='DISK'; l.data.size=size
    l.rotation_euler=(Vector(target)-l.location).to_track_quat('-Z','Y').to_euler()
    return l

def point(name, loc, color, energy, radius=1.2):
    bpy.ops.object.light_add(type='POINT', location=loc)
    l=bpy.context.object; l.name=name; l.data.energy=energy; l.data.color=color; l.data.shadow_soft_size=radius
    return l

area('Key_Warm',(0,-2,4.0),(1.0,0.42,0.18),700,8.0,(0,0,0))
area('Bar_Warm',(8,1,3.7),(1.0,0.28,0.08),500,5.0,(8,0,1))
area('DJ_Cool',(0,7,3.8),(0.08,0.45,1.0),650,5.0,(0,7,1))
area('VIP_Soft',(-7,5,3.4),(0.45,0.12,0.65),400,5.0,(-7,5,0.8))
for loc,col,en in [((-9,-6,2.0),(0.0,0.55,1.0),260),((9,-6,2.0),(1.0,0.08,0.30),260),((-8,6,2.0),(0.0,0.55,1.0),220),((8,6,2.0),(1.0,0.20,0.04),220)]:
    point('Accent_Pool',loc,col,en,1.5)

sc=bpy.context.scene
try: sc.view_settings.look='AgX - Medium High Contrast'
except Exception: pass
sc.render.resolution_x=1920; sc.render.resolution_y=1080; sc.render.resolution_percentage=70
sc.render.engine='BLENDER_EEVEE'
world=sc.world
if world:
    world.use_nodes=True
    bg=world.node_tree.nodes.get('Background')
    if bg:
        bg.inputs['Color'].default_value=(0.004,0.006,0.012,1)
        bg.inputs['Strength'].default_value=0.16

# Validation: this pass must never save a scene without the expected architecture.
mesh_names={o.name for o in bpy.data.objects if o.type=='MESH'}
required={'Floor','Wall_Back','Wall_Left','Wall_Right','Stage','BarCounter','FeatureWall'}
missing=required-mesh_names
if missing:
    raise RuntimeError('color_lighting_pass: architecture missing: '+', '.join(sorted(missing)))
if len(mesh_names) < 40:
    raise RuntimeError('color_lighting_pass: suspiciously low mesh count: %d' % len(mesh_names))

sc['mlo_visual_pass']='color_lighting_v2'
sc['mlo_visual_optimization']='preserve generated architecture; controlled lighting'
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print('COLOR/LIGHTING PASS COMPLETE:',blend if False else BLEND)
