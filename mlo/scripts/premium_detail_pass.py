import bpy, math, os
from mathutils import Vector

ROOT = r'D:\first Blender\mlo'
BLEND = os.path.join(ROOT, 'output', 'Nocturne_Lounge_MLO.blend')

bpy.ops.wm.open_mainfile(filepath=BLEND)

# Reuse the existing shared materials created by the base builder/visual pass.
def M(name, fallback=(0.15,0.15,0.15,1)):
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name); m.diffuse_color = fallback
    return m
wood=M('Wood_Walnut',(0.19,0.075,0.035,1)); metal=M('Trim_BrushedMetal',(0.22,0.24,0.26,1))
gold=M('Gold',(0.55,0.25,0.055,1)); leather=M('Leather_DeepBrown',(0.08,0.025,0.018,1))
fabric=M('Fabric_Charcoal',(0.035,0.04,0.045,1)); glass=M('Glass_Tinted',(0.025,0.08,0.10,1))
cyan=M('Neon_Cyan',(0.01,0.08,0.10,1)); mag=M('Neon_Magenta',(0.10,0.01,0.07,1)); amber=M('Neon_Amber',(0.12,0.045,0.005,1))


def cube(name, loc, scale, mat, bevel=0.0, rot=0.0):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=(0,0,rot))
    o=bpy.context.object; o.name=name; o.scale=scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod=o.modifiers.new('Detail_Bevel','BEVEL'); mod.width=bevel; mod.segments=2
    o.data.materials.append(mat); return o

def cyl(name, loc, radius, depth, mat, verts=16, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth, location=loc, rotation=rot)
    o=bpy.context.object; o.name=name; o.data.materials.append(mat); return o

def text(name, body, loc, size, mat, rot=(math.pi/2,0,0)):
    cu=bpy.data.curves.new(name,'FONT'); cu.body=body; cu.align_x='CENTER'; cu.size=size; cu.extrude=0.012; cu.bevel_depth=0.002
    o=bpy.data.objects.new(name,cu); bpy.context.collection.objects.link(o); o.location=loc; o.rotation_euler=rot; o.data.materials.append(mat); return o

# ----- grand entrance portal: layered, low-poly architectural framing -----
for x in (-7.0,7.0):
    cube('Entrance_Portal_Pillar',(x,-10.25,2.05),(0.32,0.28,2.05),wood,0.05)
    cube('Entrance_Portal_Inlay',(x,-9.92,2.05),(0.055,0.04,1.72),cyan,0.015)
cube('Entrance_Portal_Header',(0,-10.25,3.82),(7.35,0.28,0.24),wood,0.05)
cube('Entrance_Portal_Glow',(0,-9.94,3.78),(6.8,0.035,0.06),mag,0.01)
text('Entrance_Title','NOCTURNE',(0,-9.88,3.2),0.48,gold)

# ----- wall panel rhythm on the long side walls -----
for side in (-1,1):
    x=side*13.28
    for y in (-8,-4,0,4,8):
        cube('Wall_Panel',(x,y,2.1),(0.055,1.25,1.55),fabric,0.02)
        cube('Wall_Panel_Trim',(x-side*0.07,y,2.1),(0.025,1.35,1.65),gold,0.01)
        cube('Wall_Panel_Glow',(x-side*0.10,y,1.0),(0.018,0.65,0.025),cyan if y%8 else mag,0.005)

# ----- VIP privacy fins and booth tables -----
for x,y in [(-8,5.5),(-8,8.2),(4.5,-5.9),(8.0,-5.9)]:
    ang=0 if abs(x)>7 else math.pi/2
    for i in (-1,0,1):
        dx=i*0.52*math.cos(ang); dy=i*0.52*math.sin(ang)
        cube('VIP_Privacy_Fin',(x+dx,y+dy,1.55),(0.07,0.65,0.95),wood,0.025,ang)
    cyl('VIP_Table_Lamp',(x,y,1.15),0.06,0.34,amber,12)
    cyl('VIP_Lamp_Base',(x,y,0.99),0.13,0.04,gold,16)

# ----- bar detailing: illuminated bottle niches + foot rail -----
for x in (9.0,10.1,11.2):
    cube('Bottle_Niche',(x,1.74,2.55),(0.34,0.045,0.42),fabric,0.02)
    cube('Bottle_Niche_Glow',(x,1.68,2.05),(0.24,0.025,0.018),amber,0.005)
for x in (5.0,6.5,8.0,9.5,11.0):
    cyl('Bar_Foot_Rail',(x,-0.39,0.27),0.045,0.8,metal,12,rot=(0,math.pi/2,0))

# ----- stage acoustic treatment and equipment rack -----
for x in (-4.2,-3.1,-2.0,2.0,3.1,4.2):
    cube('Stage_Acoustic_Panel',(x,9.82,2.25),(0.38,0.05,0.72),fabric,0.03)
    cube('Stage_Acoustic_Inlay',(x,9.74,2.25),(0.06,0.02,0.48),mag if x<0 else cyan,0.008)
for x in (-2.8,-1.4,0,1.4,2.8):
    cyl('Stage_Downlight',(x,6.0,3.65),0.11,0.05,gold,16)

# ----- small high-value props: glasses and bottles, kept deliberately sparse -----
for x,y in [(6.8,-0.15),(8.2,-0.15),(9.6,-0.15),(7.5,0.05)]:
    cyl('Bar_Glass',(x,y,1.98),0.075,0.22,glass,12)
    cyl('Bar_Glass_Rim',(x,y,2.10),0.08,0.025,metal,12)
for x,y in [(7.1,0.2),(8.4,0.2),(9.7,0.2),(10.9,0.2)]:
    cyl('Bar_Bottle',(x,y,2.38),0.09,0.55,glass,12)
    cyl('Bar_Bottle_Neck',(x,y,2.72),0.055,0.18,glass,12)
    cyl('Bar_Bottle_Cap',(x,y,2.83),0.06,0.035,gold,12)

# ----- ceiling feature: central halo with only a few components -----
cyl('Ceiling_Center_Disc',(0,0,3.94),2.15,0.08,fabric,32)
cyl('Ceiling_Center_Inlay',(0,0,4.00),1.72,0.035,cyan,32)
for a in range(0,360,45):
    r=2.05; x=r*math.cos(math.radians(a)); y=r*math.sin(math.radians(a))
    cyl('Ceiling_Radial_Light',(x,y,4.04),0.055,0.045,mag if a%90 else amber,12)

# ----- floor wayfinding strips, useful visually and for spatial readability -----
for y in (-8.9,-6.7,6.0,8.7):
    cube('Floor_Inlay',(0,y,0.205),(5.8,0.035,0.012),gold,0.005)
for x in (-5.8,5.8):
    cube('Floor_Aisle_Inlay',(x,0,0.207),(0.025,4.8,0.012),cyan,0.005)

# ----- organize newly created objects into a detail collection -----
coll=bpy.data.collections.get('MLO_Detail') or bpy.data.collections.new('MLO_Detail')
if coll.name not in [c.name for c in bpy.context.scene.collection.children]:
    bpy.context.scene.collection.children.link(coll)
for o in list(bpy.context.scene.objects):
    if o.name.startswith(('Entrance_','Wall_Panel','VIP_','Bottle_Niche','Bar_Foot','Stage_','Bar_Glass','Bar_Bottle','Ceiling_Center','Ceiling_Radial','Floor_Inlay','Floor_Aisle')):
        for c in list(o.users_collection): c.objects.unlink(o)
        coll.objects.link(o)

# Metadata for downstream FiveM conversion tools.
scene=bpy.context.scene
scene['mlo_detail_pass']='premium_detail_v1'
scene['mlo_detail_notes']='Entrance portal, wall panels, VIP fins, bar props, stage acoustics, ceiling feature, floor inlays'
scene['fivem_target']='GTA V / FiveM'
scene['optimization_strategy']='shared materials, low-poly props, restrained light count, reusable architectural modules'

bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print('PREMIUM DETAIL PASS COMPLETE:', BLEND)
