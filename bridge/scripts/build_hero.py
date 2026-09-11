import bpy, math, os
from mathutils import Vector

ROOT=r"D:\first Blender"
OUT=os.path.join(ROOT,"bridge","output"); os.makedirs(OUT,exist_ok=True)

def M(n,c,r=.5,metal=0):
 m=bpy.data.materials.get(n) or bpy.data.materials.new(n); m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*c,1); bs.inputs['Roughness'].default_value=r; bs.inputs['Metallic'].default_value=metal
 return m

def S(o):
 if o.type=='MESH':
  for p in o.data.polygons:p.use_smooth=True

def uv(n,p,s,ma,seg=64):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=32,location=p);o=bpy.context.object;o.name=n;o.scale=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);S(o);o.data.materials.append(ma);return o

def curve(n,pts,r,ma):
 c=bpy.data.curves.new(n,'CURVE');c.dimensions='3D';c.resolution_u=16;c.bevel_depth=r;c.bevel_resolution=6
 sp=c.splines.new('BEZIER');sp.bezier_points.add(len(pts)-1)
 for b,q in zip(sp.bezier_points,pts):b.co=q;b.handle_left_type='AUTO';b.handle_right_type='AUTO'
 o=bpy.data.objects.new(n,c);bpy.context.collection.objects.link(o);o.data.materials.append(ma);return o

def cyl(n,a,b,r,ma):
 a,b=Vector(a),Vector(b);d=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=r,depth=d.length,location=(a+b)/2);o=bpy.context.object;o.name=n;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();S(o);o.data.materials.append(ma);return o

def look(o,t):o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()

def noise_mat(n,c1,c2,scale=3):
 m=M(n,c1,.62);nt=m.node_tree;bs=nt.nodes['Principled BSDF'];tex=nt.nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=scale;tex.inputs['Detail'].default_value=4;tex.inputs['Roughness'].default_value=.65;ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(*c1,1);ramp.color_ramp.elements[1].color=(*c2,1);nt.links.new(tex.outputs['Fac'],ramp.inputs['Fac']);nt.links.new(ramp.outputs['Color'],bs.inputs['Base Color']);return m

bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
# palette
skin=noise_mat('Milo Skin',(0.42,.50,.53),(.60,.67,.69),5); skin2=M('Inner Ear',(.90,.48,.52),.72); eye=M('Eye',(1,.99,.94),.22); pupil=M('Pupil',(.008,.006,.005),.18); white=M('Tusk',(.94,.78,.48),.35); red=M('Scarf',(.96,.16,.07),.55); mouth=M('Mouth',(.07,.008,.01),.4); tongue=M('Tongue',(.98,.25,.34),.5); ground=noise_mat('Ground',(.12,.34,.07),(.24,.55,.13),7); leaf=M('Leaf',(.08,.32,.07),.72); leaf2=M('Leaf Light',(.22,.56,.13),.75); bark=noise_mat('Bark',(.20,.07,.025),(.42,.18,.06),4); flower=M('Flower', (1,.72,.05),.5); cloud=M('Cloud',(1,1,1),.9)
# ground bevelled layers
bpy.ops.mesh.primitive_plane_add(size=60,location=(0,0,-.02));bpy.context.object.data.materials.append(ground)
for x,y,s in [(-8,3,1.4),(8,4,1.2),(-7,-1,.9),(7,-2,1)]:
 cyl('Trunk',(x,y,0),(x,y,2.8*s),.28*s,bark)
 for a,b in [((x,y,1.5*s),(x-.8*s,y,2.3*s)),((x,y,1.7*s),(x+.75*s,y,2.5*s))]:cyl('Branch',a,b,.11*s,bark)
 for dx,dy,dz,ss,ma in [(-.7,0,2.9,.9,leaf),(0,0,3.3,1,leaf2),(.7,0,3,.9,leaf)]:uv('Tree Crown',(x+dx*s,y+dy*s,dz*s),(1.15*ss*s,.95*ss*s,1.0*ss*s),ma,48)
# distant soft hills
for x,y,s in [(-13,4,4),(12,6,5),(0,9,6)]:uv('Hill',(x,y,.4),(s,2.0,.9),leaf2,48)
# flowers / foreground detail
for i in range(38):
 x=-10+(i*1.71)%20;y=-2+(i*2.17)%9
 cyl('Stem',(x,y,.02),(x,y,.34),.012,leaf2)
 for k in range(5):
  a=k*math.tau/5;uv('Petal',(x+math.cos(a)*.075,y+math.sin(a)*.075,.38),(.065,.045,.05),flower,24)
# Milo, larger and better proportions
uv('Body',(0,0,1.48),(1.02,.78,1.18),skin);uv('Belly',(0,-.68,1.45),(.70,.18,.78),M('Belly',(.54,.62,.64),.75),48)
for x in [-.52,.52]:
 uv('Leg',(x,0,.72),(.34,.43,.68),skin);uv('Foot',(x,-.18,.32),(.48,.55,.25),skin)
# head
uv('Head',(0,-.03,3.02),(1.30,1.02,1.08),skin)
for x in [-1.22,1.22]:uv('Ear',(x,.0,3.08),(.65,.18,.83),skin);uv('Inner Ear',(x,-.19,3.08),(.42,.055,.59),skin2)
# eyes with catchlights and brows
for x in [-.46,.46]:
 uv('Eye',(x,-.95,3.34),(.29,.11,.32),eye);uv('Pupil',(x,-1.055,3.34),(.12,.035,.15),pupil);uv('Catchlight',(x-.045,-1.09,3.43),(.035,.012,.045),eye,24)
 curve('Brow',[(x-.20,-1.08,3.69),(x,-1.12,3.77),(x+.20,-1.08,3.69)],.035,pupil)
uv('Cheek L',(-.66,-.96,2.84),(.21,.055,.17),M('Cheek',(.90,.38,.42),.7),32);uv('Cheek R',(.66,-.96,2.84),(.21,.055,.17),bpy.data.materials['Cheek'],32)
curve('Trunk',[(0,-.98,3.02),(0,-1.25,2.76),(-.08,-1.33,2.47),(.12,-1.27,2.28)],.245,skin);uv('Trunk Tip',(.12,-1.27,2.28),(.27,.19,.17),skin)
for x in [-.27,.27]:
 o=cyl('Tusk',(x,-1.12,2.52),(x*.75,-1.30,2.14),.085,white)
# mouth smile
uv('Mouth',(0,-1.01,2.72),(.42,.045,.21),mouth,48);uv('Tongue',(0,-1.065,2.64),(.21,.025,.08),tongue,32)
# arms + fingers
for x in [-1,1]:
 cyl('Arm',(x*.72,-.02,1.90),(x*1.08,-.35,1.25),.22,skin);uv('Hand',(x*1.10,-.38,1.23),(.30,.23,.24),skin)
 for k in [-.09,0,.09]:uv('Finger',(x*1.10+k,-.57,1.20),(.045,.035,.065),skin,24)
# scarf ribbon and knot
curve('Scarf',[(-.82,-.18,2.35),(-.42,-.48,2.27),(0,-.52,2.24),(.42,-.48,2.27),(.82,-.18,2.35)],.12,red);uv('Knot',(0,-.57,2.23),(.22,.12,.18),red)
# tail
curve('Tail',[(.90,.30,1.55),(1.35,.52,1.30),(1.58,.50,1.02)],.085,skin);uv('Tail Tip',(1.58,.50,1.02),(.13,.11,.17),skin)
# butterflies as proper 3D silhouettes
but=M('Butterfly',(.15,.32,.95),.48)
for x,y,z in [(-3,-1,2.8),(3,1,3.6),(4,-1,2.7)]:
 cyl('Butterfly Body',(x,y,z-.14),(x,y,z+.14),.018,pupil);uv('WingL',(x-.14,y,z),(.17,.025,.11),but,32);uv('WingR',(x+.14,y,z),(.17,.025,.11),but,32)
# clouds, background depth
for x,y,z,s in [(-8,5,8,1.0),(2,7,8.2,.9),(9,3,7.6,.75)]:
 for dx,dz,ss in [(-.75,0,.7),(0,.25,1),(.75,0,.7)]:uv('Cloud',(x+dx*s,y,z+dz*s),(1.0*ss*s,.5*s,.45*ss*s),cloud,32)
# camera close cinematic
bpy.ops.object.camera_add(location=(7.1,-14.8,5.35));cam=bpy.context.object;cam.data.lens=58;cam.data.sensor_width=36;cam.data.dof.use_dof=True;cam.data.dof.focus_object=bpy.data.objects['Head'];cam.data.dof.aperture_fstop=2.8;look(cam,(0,-.05,2.45));bpy.context.scene.camera=cam
# lighting: soft key/fill/rim + sun
for n,loc,en,size in [('Key',(4,-6,9),1300,5.0),('Fill',(-5,-4,5),500,6.0),('Rim',(2,5,7),1200,4.0)]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.name=n;l.data.energy=en;l.data.shape='DISK';l.data.size=size;look(l,(0,0,2))
bpy.ops.object.light_add(type='SUN',location=(0,0,8));sun=bpy.context.object;sun.data.energy=1.5;sun.rotation_euler=(math.radians(25),math.radians(-20),math.radians(-25))
# world / color management
w=bpy.context.scene.world;w.use_nodes=True;w.node_tree.nodes['Background'].inputs['Color'].default_value=(.12,.28,.48,1);w.node_tree.nodes['Background'].inputs['Strength'].default_value=.28
sc=bpy.context.scene;sc.render.engine='BLENDER_EEVEE';sc.render.resolution_x=1920;sc.render.resolution_y=1080;sc.render.resolution_percentage=75;sc.render.image_settings.file_format='PNG';sc.render.film_transparent=False;sc.render.fps=24;sc.frame_start=1;sc.frame_end=120
try:sc.view_settings.look='AgX - Medium High Contrast'
except:pass
# subtle breathing / wave animation
for obj,idx,vals in [(bpy.data.objects.get('Arm'),2,[0])]:pass
head=bpy.data.objects['Head'];head.rotation_euler[2]=math.radians(-2);head.keyframe_insert('rotation_euler',index=2,frame=1);head.rotation_euler[2]=math.radians(2);head.keyframe_insert('rotation_euler',index=2,frame=60);head.rotation_euler[2]=math.radians(-2);head.keyframe_insert('rotation_euler',index=2,frame=120)
sc.render.filepath=os.path.join(OUT,'hero_quality.png');bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'hero_quality.blend'));bpy.ops.render.render(write_still=True);print('HERO QUALITY BUILD COMPLETE')
