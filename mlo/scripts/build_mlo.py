import bpy, math, os, json
from mathutils import Vector

ROOT = r'D:\first Blender\mlo'
OUT = os.path.join(ROOT, 'output')
os.makedirs(OUT, exist_ok=True)

# ---------- reset ----------
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for datablocks in (bpy.data.materials, bpy.data.curves, bpy.data.meshes, bpy.data.cameras, bpy.data.lights):
    pass

# ---------- materials ----------
def mat(name, color, metallic=0.0, rough=0.45, emission=None, strength=0.0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Metallic'].default_value=metallic
    bs.inputs['Roughness'].default_value=rough
    if emission:
        bs.inputs['Emission Color'].default_value=(*emission,1)
        bs.inputs['Emission Strength'].default_value=strength
    return m

MAT={
 'floor':mat('Floor_DarkStone',(0.055,0.065,0.075),0.25,0.25),
 'wall':mat('Wall_WarmConcrete',(0.12,0.105,0.10),0.0,0.62),
 'trim':mat('Trim_BrushedMetal',(0.22,0.24,0.26),0.8,0.22),
 'wood':mat('Wood_Walnut',(0.19,0.075,0.035),0.05,0.32),
 'leather':mat('Leather_DeepBrown',(0.08,0.025,0.018),0.0,0.32),
 'fabric':mat('Fabric_Charcoal',(0.035,0.04,0.045),0.0,0.82),
 'glass':mat('Glass_Tinted',(0.025,0.08,0.10),0.55,0.08),
 'gold':mat('Gold',(0.55,0.25,0.055),0.9,0.16),
 'neon_cyan':mat('Neon_Cyan',(0.01,0.08,0.10),0.0,0.25,(0.0,0.9,1.0),8),
 'neon_magenta':mat('Neon_Magenta',(0.10,0.01,0.07),0.0,0.25,(1.0,0.02,0.45),8),
 'neon_amber':mat('Neon_Amber',(0.12,0.045,0.005),0.0,0.25,(1.0,0.18,0.01),6),
 'green':mat('Plant_Green',(0.025,0.12,0.045),0.0,0.7),
 'white':mat('Display_White',(0.75,0.78,0.82),0.0,0.3),
}

def cube(name, loc, scale, material, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod=o.modifiers.new('Soft_Edges','BEVEL'); mod.width=bevel; mod.segments=3
    o.data.materials.append(material)
    return o

def cyl(name, loc, radius, depth, material, verts=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth, location=loc)
    o=bpy.context.object; o.name=name; o.data.materials.append(material)
    return o

def uv(name, loc, scale, material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True); o.data.materials.append(material); return o

def torus(name, loc, major, minor, material, rot=(0,0,0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, major_segments=48, minor_segments=12, location=loc, rotation=rot)
    o=bpy.context.object; o.name=name; o.data.materials.append(material); return o

def text(name, body, loc, size, material, rot=(math.pi/2,0,0), extrude=0.015):
    cu=bpy.data.curves.new(name,'FONT'); cu.body=body; cu.align_x='CENTER'; cu.size=size; cu.extrude=extrude; cu.bevel_depth=0.004
    o=bpy.data.objects.new(name,cu); bpy.context.collection.objects.link(o); o.location=loc; o.rotation_euler=rot; o.data.materials.append(material); return o

# ---------- architecture ----------
# 28m x 22m premium underground lounge, 4.2m ceiling
cube('Floor',(0,0,0),(14,11,0.18),MAT['floor'],0.06)
# perimeter walls, with open front/reception entry
cube('Wall_Back',(0,10.7,2.1),(14,0.35,2.1),MAT['wall'],0.08)
cube('Wall_Left',(-13.7,0,2.1),(0.35,10.7,2.1),MAT['wall'],0.08)
cube('Wall_Right',(13.7,0,2.1),(0.35,10.7,2.1),MAT['wall'],0.08)
# partial front walls leaving grand opening
cube('Wall_Front_L',(-10.5,-10.7,2.1),(3.2,0.35,2.1),MAT['wall'],0.08)
cube('Wall_Front_R',(10.5,-10.7,2.1),(3.2,0.35,2.1),MAT['wall'],0.08)
# ceiling beams
for x in (-9,-3,3,9): cube('Ceiling_Beam',(x,0,4.1),(0.16,10.2,0.18),MAT['trim'],0.03)
for y in (-7,0,7): cube('Ceiling_Beam',(0,y,4.05),(13.4,0.12,0.12),MAT['trim'],0.02)
# architectural wall slats
for x in range(-11,12,2): cube('Wall_Slat',(x,10.25,2.2),(0.035,0.08,1.7),MAT['gold'],0.01)

# ---------- stage / DJ ----------
cube('Stage',(0,7.4,0.45),(5.2,2.1,0.45),MAT['wood'],0.10)
cube('Stage_Fascia',(0,5.35,0.45),(5.2,0.08,0.35),MAT['neon_cyan'],0.03)
cube('DJ_Desk',(0,7.0,1.35),(3.5,0.55,0.55),MAT['fabric'],0.08)
for x in (-2.2,-1.1,0,1.1,2.2): cube('DJ_LED',(x,6.4,1.35),(0.08,0.02,0.3),MAT['neon_magenta'],0.02)
for x in (-3.8,3.8):
    cube('Speaker',(x,7.8,1.8),(0.55,0.45,1.3),MAT['fabric'],0.08)
    for z in (1.3,1.9,2.5): torus('SpeakerRing',(x,7.3,z),0.24,0.035,MAT['neon_cyan'],(math.pi/2,0,0))

# ---------- bar ----------
cube('BarCounter',(8.3,0.4,1.0),(4.2,0.75,0.75),MAT['wood'],0.14)
cube('BarTop',(8.3,0.4,1.82),(4.35,0.82,0.10),MAT['gold'],0.05)
cube('BarBack',(11.7,2.0,2.1),(0.25,2.2,2.0),MAT['wood'],0.06)
for z in (1.0,1.8,2.6,3.3): cube('BarShelf',(11.35,2.0,z),(0.15,1.85,0.06),MAT['trim'],0.02)
for x in (9.0,10.1,11.2):
    cyl('Bottle',(x,1.8,2.35),0.10,0.65,MAT['glass'])
    cyl('BottleCap',(x,1.8,2.72),0.11,0.05,MAT['gold'])
for x in (6.3,7.8,9.3,10.8):
    cyl('BarStool',(x,-0.65,0.55),0.28,0.9,MAT['gold'])
    cyl('StoolSeat',(x,-0.65,1.02),0.38,0.12,MAT['leather'])

# ---------- VIP lounge ----------
def sofa(x,y,rot=0):
    o=cube('VIP_Sofa',(x,y,0.75),(1.7,0.55,0.45),MAT['leather'],0.20); o.rotation_euler[2]=rot
    for dx in (-1.45,1.45):
        a=cube('SofaArm',(x+dx*math.cos(rot),y+dx*math.sin(rot),1.05),(0.25,0.62,0.7),MAT['leather'],0.12); a.rotation_euler[2]=rot
    return o
sofa(-8,4.0); sofa(-8,7.0); sofa(4.5,-5.8); sofa(8,-5.8)
for x,y in [(-5.7,5.5),(6.0,-4.0)]:
    cyl('LowTable',(x,y,0.45),0.9,0.12,MAT['gold'])
    cyl('TableGlass',(x,y,0.58),0.75,0.06,MAT['glass'])

# ---------- dining / tables ----------
for x in (-3.5,0,3.5):
    cube('DiningTable',(x,-3.4,0.78),(1.25,0.65,0.08),MAT['wood'],0.08)
    for sx in (-0.95,0.95):
        for sy in (-0.85,0.85):
            cyl('ChairLeg',(x+sx,-3.4+sy*0.45,0.4),0.045,0.7,MAT['gold'],16)
            cube('ChairSeat',(x+sx,-3.4+sy*0.45,0.82),(0.38,0.38,0.08),MAT['leather'],0.08)

# ---------- feature wall / logo ----------
cube('FeatureWall',(0,10.15,2.15),(6.5,0.12,1.8),MAT['fabric'],0.03)
text('Logo','NOCTURNE',(0,9.98,2.55),1.05,MAT['neon_cyan'],(math.pi/2,0,0),0.025)
for x in (-5.7,5.7): torus('WallHalo',(x,9.9,2.3),0.85,0.06,MAT['neon_magenta'],(math.pi/2,0,0))

# ---------- plants ----------
for x,y in [(-11,-6),(-11,6),(11,-6),(11,6),(5,5)]:
    cyl('PlantPot',(x,y,0.45),0.5,0.75,MAT['wood'])
    for i in range(9):
        a=i*0.7; z=1.2+0.35*(i%3)
        uv('Leaf',(x+0.4*math.cos(a),y+0.4*math.sin(a),z),(0.18,0.5,0.06),MAT['green']).rotation_euler[2]=a

# ---------- decorative lighting fixtures ----------
for x in (-9,-3,3,9):
    for y in (-7,0,7):
        cyl('CeilingFixture',(x,y,3.8),0.22,0.08,MAT['neon_amber'])
        bpy.ops.object.light_add(type='AREA', location=(x,y,3.65))
        l=bpy.context.object; l.name='Warm_Ceiling_Light'; l.data.energy=280; l.data.shape='DISK'; l.data.size=2.0; l.data.color=(1.0,0.34,0.10)
        l.rotation_euler=(0,0,0)
# accent point lights
for loc,color,energy in [((-9,0,1.8),(0.0,0.65,1.0),450),((0,5,2.0),(1.0,0.02,0.3),550),((9,0,1.8),(0.0,0.65,1.0),450),((0,-7,2.0),(1.0,0.18,0.02),350)]:
    bpy.ops.object.light_add(type='POINT',location=loc); l=bpy.context.object; l.data.energy=energy; l.data.color=color; l.data.shadow_soft_size=1.4

# world
world=bpy.context.scene.world
world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.006,0.008,0.012,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=0.22

# ---------- camera ----------
bpy.ops.object.camera_add(location=(18,-24,12))
cam=bpy.context.object; cam.name='MLO_Showcase_Camera'; bpy.context.scene.camera=cam

def look_at(obj, target): obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
look_at(cam,(0,1,1.5)); cam.data.lens=28

# ---------- render ----------
sc=bpy.context.scene
sc.render.engine='BLENDER_EEVEE'
sc.render.resolution_x=1920; sc.render.resolution_y=1080; sc.render.resolution_percentage=70
sc.render.image_settings.file_format='PNG'
sc.render.film_transparent=False
# color management
try:
    sc.view_settings.look='AgX - Medium High Contrast'
except: pass
sc.render.filepath=os.path.join(OUT,'mlo_showcase.png')

# ---------- collections / metadata ----------
for cname in ('MLO_Geometry','MLO_Props','MLO_Lighting','MLO_Collision','MLO_Interior'):
    if cname not in bpy.data.collections: bpy.data.collections.new(cname)
meta={
 'name':'Nocturne Lounge',
 'type':'FiveM MLO',
 'dimensions_m':[28,22,4.2],
 'rooms':['Main Lounge','Bar','DJ Stage','VIP Lounge','Back Bar'],
 'target':'GTA V / FiveM',
 'pipeline':'Blender -> Sollumz/CodeWalker -> YMAP/YTYP/YBN',
 'status':'blockout + detailed asset pass',
 'notes':'Original design; optimized game-ready workflow planned.'
}
with open(os.path.join(OUT,'mlo_manifest.json'),'w',encoding='utf-8') as f: json.dump(meta,f,indent=2)

# save blend
blend=os.path.join(OUT,'Nocturne_Lounge_MLO.blend')
bpy.ops.wm.save_as_mainfile(filepath=blend)
# render showcase
bpy.ops.render.render(write_still=True)
print('MLO BUILD COMPLETE:', blend)
