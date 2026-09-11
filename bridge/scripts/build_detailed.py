import bpy
import math
import os
import mathutils
from mathutils import Vector

PROJECT_DIR = r"D:\first Blender"
OUTPUT_DIR = os.path.join(PROJECT_DIR, "bridge", "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------- helpers ----------
def mat(name, color, rough=0.65, metallic=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1)
        bsdf.inputs["Roughness"].default_value = rough
        bsdf.inputs["Metallic"].default_value = metallic
    m.diffuse_color = (*color, 1)
    return m

def smooth(o):
    if o.type == 'MESH':
        for p in o.data.polygons: p.use_smooth = True

def uv(name, loc, scale, material, seg=48):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=24, location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    smooth(o); o.data.materials.append(material)
    return o

def cube(name, loc, scale, material, bevel=.15):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        b=o.modifiers.new("Rounded edges",'BEVEL'); b.width=bevel; b.segments=4
    o.data.materials.append(material); return o

def cone(name, loc, r1, r2, depth, material):
    bpy.ops.mesh.primitive_cone_add(vertices=48, radius1=r1, radius2=r2, depth=depth, location=loc)
    o=bpy.context.object; o.name=name; smooth(o); o.data.materials.append(material); return o

def cyl_between(name, a, b, radius, material):
    a,b=Vector(a),Vector(b); d=b-a
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=d.length, location=(a+b)/2)
    o=bpy.context.object; o.name=name; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); smooth(o); o.data.materials.append(material); return o

def look_at(obj, target):
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()

def curve_line(name, points, bevel, material):
    cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'; cu.bevel_depth=bevel; cu.bevel_resolution=5; cu.resolution_u=12
    sp=cu.splines.new('BEZIER'); sp.bezier_points.add(len(points)-1)
    for p,co in zip(sp.bezier_points,points):
        p.co=co; p.handle_left_type='AUTO'; p.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,cu); bpy.context.collection.objects.link(o); o.data.materials.append(material); return o

# ---------- clean ----------
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for datablocks in (bpy.data.curves, bpy.data.cameras, bpy.data.lights):
    pass

# ---------- materials ----------
sky=mat('Sky',(0.36,0.70,1.0),.8)
grass=mat('Grass',(0.16,0.48,0.12),.9)
grass2=mat('Grass Detail',(0.28,0.65,0.16),.85)
leaf=mat('Leaves',(0.08,0.34,0.08),.8)
leaf2=mat('Leaf Light',(0.18,0.52,0.10),.8)
trunk=mat('Tree Bark',(0.30,0.12,0.045),.9)
rock=mat('Rock',(0.32,0.36,0.32),.95)
elephant=mat('Milo Warm Gray',(0.52,0.60,0.62),.7)
elephant2=mat('Milo Ear Inner',(0.82,0.48,0.50),.72)
white=mat('Eye White',(0.98,0.98,0.95),.4)
black=mat('Pupil',(0.015,0.012,0.01),.25)
mouth=mat('Mouth',(0.08,0.015,0.012),.55)
tongue=mat('Tongue',(0.95,0.25,0.30),.6)
tusk=mat('Tusks',(0.95,0.83,0.55),.45)
scarf=mat('Scarf',(0.95,0.25,0.08),.72)
yellow=mat('Flower Yellow',(1.0,0.78,0.08),.55)
whiteflower=mat('Flower White',(1.0,.95,.82),.55)

# ---------- meadow ----------
bpy.ops.mesh.primitive_plane_add(size=40, location=(0,0,0))
g=bpy.context.object; g.name='Meadow Ground'; g.data.materials.append(grass)

# small grass clusters
for i in range(55):
    x=-11+(i*1.73)%22; y=-2+(i*2.41)%12
    if abs(x)<2.3 and -2<y<2.5: continue
    for j in range(3):
        xx=x+(j-1)*.09
        o=cone('Grass Blade',(xx,y,.16),.035,.005,.32,grass2); o.rotation_euler[1]=(j-1)*.22

# flowers
for i in range(18):
    x=-9+(i*2.7)%18; y=-1+(i*3.1)%8
    cyl_between('Flower Stem',(x,y,.02),(x,y,.35),.018,grass2)
    for a in range(5):
        ang=a*math.tau/5
        uv('Petal',(x+math.cos(ang)*.10,y+math.sin(ang)*.10,.39),(.075,.045,.06), yellow if i%2==0 else whiteflower,24)
    uv('Flower Center',(x,y,.40),(.065,.065,.05),yellow,24)

# rocks
for x,y,s in [(-5,-1,.7),(5,1,.5),(7,-2,.35),(-7,2,.45)]:
    o=uv('Rounded Rock',(x,y,.25),(s,.7*s,.35*s),rock,32); o.rotation_euler[2]=.2

# ---------- trees with branches and layered crowns ----------
def tree(x,y,s=1):
    cyl_between('Tree Trunk',(x,y,.05),(x,y,2.25*s),.34*s,trunk)
    cyl_between('Branch',(x,y,1.45*s),(x-.75*s,y,2.0*s),.12*s,trunk)
    cyl_between('Branch',(x,y,1.55*s),(x+.7*s,y,2.15*s),.11*s,trunk)
    uv('Crown A',(x-.65*s,y,2.45*s),(1.15*s,1.0*s,1.0*s),leaf,32)
    uv('Crown B',(x+.55*s,y,2.55*s),(1.25*s,1.05*s,1.1*s),leaf2,32)
    uv('Crown C',(x,y,3.15*s),(1.2*s,1.0*s,.95*s),leaf,32)
for t in [(-6,3,1.25),(6,4,1.05),(-7,-1,.8),(7,-2,.9)]: tree(*t)

# ---------- hero: detailed baby elephant ----------
# legs/body
uv('Milo Body',(0,0,1.55),(1.05,.82,1.28),elephant)
uv('Milo Belly',(0,-.68,1.55),(.72,.22,.82),mat('Belly',(0.62,.69,.70),.72),32)
for x in (-.55,.55):
    uv('Milo Leg',(x,0,.72),(.38,.46,.72),elephant)
    uv('Milo Foot',(x,-.18,.34),(.46,.55,.25),elephant)
    for dx in (-.14,0,.14): uv('Toenail',(x+dx,-.67,.37),(.055,.035,.045),tusk,20)
# head
uv('Milo Head',(0,-.02,3.05),(1.28,1.05,1.05),elephant)
# ears
for x,side in [(-1.22,'L'),(1.22,'R')]:
    uv(f'Outer Ear {side}',(x,.02,3.10),(.62,.18,.82),elephant)
    uv(f'Inner Ear {side}',(x,-.18,3.10),(.40,.07,.58),elephant2)
# eyes, eyelids, brows
for x,side in [(-.46,'L'),(.46,'R')]:
    uv(f'Eye {side}',(x,-.96,3.30),(.28,.10,.31),white,32)
    uv(f'Pupil {side}',(x,-1.045,3.30),(.115,.045,.14),black,24)
    curve_line(f'Brow {side}',[(x-.20,-1.08,3.68),(x,-1.11,3.75),(x+.20,-1.08,3.68)],.035,black)
# cheeks
uv('Left Cheek',(-.63,-.93,2.84),(.22,.07,.18),mat('Cheek',(0.82,.42,.44),.75),24)
uv('Right Cheek',(.63,-.93,2.84),(.22,.07,.18),bpy.data.materials['Cheek'],24)
# trunk as curved segments
curve_line('Milo Trunk',[(0,-.98,3.02),(0,-1.25,2.70),(-.05,-1.30,2.38),(.10,-1.24,2.22)],.25,elephant)
uv('Trunk Tip',(.10,-1.24,2.21),(.28,.20,.18),elephant,32)
# tusks
for x in (-.28,.28):
    o=cone('Tusk',(x,-1.18,2.45),.10,.025,.55,tusk); o.rotation_euler[0]=math.radians(28)
# mouth and tongue
uv('Open Mouth',(0,-1.04,2.67),(.40,.055,.20),mouth,32)
uv('Tongue',(0,-1.10,2.61),(.22,.035,.09),tongue,24)
# arms and hands
for x in (-1.02,1.02):
    cyl_between('Arm',(x*.72,-.02,1.90),(x*1.08,-.25,1.30),.24,elephant)
    uv('Hand',(x*1.10,-.30,1.27),(.30,.24,.25),elephant,32)
    for k in (-.10,0,.10): uv('Finger',(x*1.10+k,-.53,1.25),(.055,.04,.07),elephant,20)
# scarf with knot
curve_line('Scarf Collar',[(-.75,-.10,2.32),(-.35,-.45,2.25),(0,-.50,2.22),(.35,-.45,2.25),(.75,-.10,2.32)],.13,scarf)
uv('Scarf Knot',(0,-.55,2.23),(.22,.12,.20),scarf,24)
# tail
curve_line('Tail',[(.92,.30,1.55),(1.45,.55,1.35),(1.65,.50,1.00)],.10,elephant)
uv('Tail Tip',(1.65,.50,1.0),(.15,.13,.20),elephant,24)

# ---------- butterflies ----------
butter=mat('Butterfly',(0.2,.35,1.0),.55)
for x,y,z in [(-3,-1,2.5),(3,1,3.4),(4,-1,2.7)]:
    cyl_between('Butterfly Body',(x,y,z-.12),(x,y,z+.12),.025,black)
    uv('Wing L',(x-.16,y,z),(.17,.035,.11),butter,20)
    uv('Wing R',(x+.16,y,z),(.17,.035,.11),butter,20)

# ---------- clouds ----------
cloud=mat('Cloud',(1,1,1),.9)
for x,y,z,s in [(-7,4,8,1.0),(4,6,7.5,.8),(8,2,8,.65)]:
    for dx,dz,ss in [(-.8,0,.7),(0,.25,1),(0.8,0,.7)]:
        uv('Cloud',(x+dx*s,y,z+dz*s),(1.0*ss*s,.45*s,.45*ss*s),cloud,24)

# ---------- camera ----------
bpy.ops.object.camera_add(location=(8.8,-15.5,6.4))
cam=bpy.context.object; cam.name='Cinematic Camera'; cam.data.lens=55; cam.data.dof.use_dof=True; cam.data.dof.focus_object=bpy.data.objects['Milo Head']; cam.data.dof.aperture_fstop=3.2
look_at(cam,(0,0,2.25)); bpy.context.scene.camera=cam

# ---------- lighting ----------
def area(name,loc,energy,size):
    bpy.ops.object.light_add(type='AREA',location=loc); l=bpy.context.object; l.name=name; l.data.energy=energy; l.data.shape='DISK'; l.data.size=size; look_at(l,(0,0,2)); return l
area('Key Softbox',(4,-6,9),1100,5.5)
area('Fill Softbox',(-5,-4,5),650,6)
area('Rim Light',(2,5,7),1000,4)
# sun for readable outdoor shadows
bpy.ops.object.light_add(type='SUN',location=(0,0,8)); sun=bpy.context.object; sun.name='Warm Sun'; sun.data.energy=2.0; sun.rotation_euler=(math.radians(25),math.radians(-20),math.radians(-25))

# ---------- world / render ----------
world=bpy.context.scene.world
world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.22,.48,.78,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35
scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=1920; scene.render.resolution_y=1080; scene.render.resolution_percentage=60
scene.render.image_settings.file_format='PNG'
scene.render.film_transparent=False
scene.render.filepath=os.path.join(OUTPUT_DIR,'detailed_test.png')
scene.render.fps=24; scene.frame_start=1; scene.frame_end=72
# color management
try:
    scene.view_settings.look='AgX - Medium High Contrast'
except Exception: pass

# subtle animation: trunk sway and wave
trunk_obj=bpy.data.objects.get('Milo Trunk')
if trunk_obj:
    trunk_obj.rotation_euler[2]=0.0; trunk_obj.keyframe_insert(data_path='rotation_euler',index=2,frame=1)
    trunk_obj.rotation_euler[2]=math.radians(5); trunk_obj.keyframe_insert(data_path='rotation_euler',index=2,frame=36)
    trunk_obj.rotation_euler[2]=math.radians(-3); trunk_obj.keyframe_insert(data_path='rotation_euler',index=2,frame=72)

# save and render preview
blend_path=os.path.join(OUTPUT_DIR,'detailed_test.blend')
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
scene.render.filepath=os.path.join(OUTPUT_DIR,'detailed_test.png')
bpy.ops.render.render(write_still=True)
print('DETAILED TEST COMPLETE:',blend_path)
