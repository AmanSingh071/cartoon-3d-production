import bpy, os, math, wave, struct, subprocess
from mathutils import Vector

PROJECT=r'D:\first Blender'
OUT=os.path.join(PROJECT,'bridge','output'); AUDIO=os.path.join(PROJECT,'bridge','audio')
os.makedirs(OUT,exist_ok=True); os.makedirs(AUDIO,exist_ok=True)
FPS=24; END=FPS*600

# Reuse the proven hero asset generator, then turn it into a complete animated episode.
hero=os.path.join(PROJECT,'bridge','scripts','build_hero.py')
exec(compile(open(hero,'r',encoding='utf-8').read(),hero,'exec'))
scene=bpy.context.scene; scene.name='EPISODE_RENDER'; scene.render.engine='BLENDER_EEVEE_NEXT'
scene.render.resolution_x=1920; scene.render.resolution_y=1080; scene.render.resolution_percentage=100
scene.render.fps=FPS; scene.frame_start=1; scene.frame_end=END
scene.render.image_settings.file_format='FFMPEG'; scene.render.ffmpeg.format='MPEG4'; scene.render.ffmpeg.codec='H264'; scene.render.ffmpeg.constant_rate_factor='HIGH'; scene.render.ffmpeg.audio_codec='AAC'; scene.render.ffmpeg.audio_bitrate=192
scene.render.filepath=os.path.join(OUT,'milo_and_the_moonflower.mp4')

# Helpers
def look(o,t): o.rotation_euler=(Vector(t)-o.location).to_track_quat('-Z','Y').to_euler()
def k(o,path,frame,val,index=None):
    if index is None: setattr(o,path,val); o.keyframe_insert(data_path=path,frame=frame)
    else: getattr(o,path).__setitem__(index,val); o.keyframe_insert(data_path=path,index=index,frame=frame)
def keycam(sec,pos,target,lens):
    f=int(sec*FPS); cam.location=pos; look(cam,target); cam.data.lens=lens
    cam.keyframe_insert(data_path='location',frame=f); cam.keyframe_insert(data_path='rotation_euler',frame=f); cam.data.keyframe_insert(data_path='lens',frame=f)

def mkmat(n,c,r=.6):
    m=bpy.data.materials.get(n) or bpy.data.materials.new(n); m.diffuse_color=(*c,1); m.use_nodes=True; bs=m.node_tree.nodes.get('Principled BSDF')
    if bs: bs.inputs['Base Color'].default_value=(*c,1); bs.inputs['Roughness'].default_value=r
    return m

def sphere(n,loc,sc,mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=20,location=loc); o=bpy.context.object; o.name=n; o.scale=sc; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for p in o.data.polygons:p.use_smooth=True
    o.data.materials.append(mat); return o

def cyl(a,b,r,mat,n='detail'):
    a,b=Vector(a),Vector(b); d=b-a; bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=r,depth=d.length,location=(a+b)/2); o=bpy.context.object; o.name=n; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.data.materials.append(mat); return o

# Additional supporting character and story props.
rabbit=mkmat('Pip Fur',(.92,.86,.75),.7); inner=mkmat('Pip Inner',(.96,.57,.64),.65); white=mkmat('Eye White',(1,.99,.94),.25); dark=mkmat('Pupil',(.01,.008,.006),.15); pink=mkmat('Pip Cheeks',(.92,.36,.42),.65); blue=mkmat('Pip Vest',(.12,.45,.86),.58); gold=mkmat('Magic Gold',(1,.62,.08),.28)
root=bpy.data.objects.new('PIP_RIG',None); bpy.context.collection.objects.link(root); root.location=(7,-4,0)
parts=[]
parts += [sphere('Pip Body',(0,0,1.35),(.70,.58,.98),rabbit),sphere('Pip Head',(0,-.02,2.52),(.82,.68,.72),rabbit)]
for x in (-.44,.44):
    parts += [sphere('Pip Ear',(x,.02,3.30),(.24,.18,.70),rabbit),sphere('Pip Inner Ear',(x,-.17,3.30),(.13,.05,.50),inner),sphere('Pip Eye',(x*.55,-.64,2.67),(.16,.07,.18),white),sphere('Pip Pupil',(x*.55,-.70,2.67),(.07,.025,.09),dark)]
parts += [sphere('Pip Nose',(0,-.67,2.43),(.10,.05,.07),pink),sphere('Pip Vest',(0,-.53,1.55),(.58,.10,.58),blue),sphere('Pip Tail',(.65,.35,1.38),(.24,.20,.24),rabbit)]
for x in (-1,1): parts += [cyl((x*.55,0,1.55),(x*.92,-.22,1.08),.15,rabbit,'Pip Arm'),sphere('Pip Foot',(x*.52,-.18,.34),(.32,.38,.20),rabbit)]
for o in parts:o.parent=root

# Magic seed, flower and glowing fireflies.
seed=sphere('Magic Seed',(0,-.8,.50),(.12,.12,.17),gold); flower=sphere('Moonflower',(0,-.75,1.65),(.38,.38,.20),mkmat('Moonflower',(1,.94,.70),.25)); flower.scale=(.03,.03,.03)
for i in range(18):
    a=i*math.tau/18; f=sphere('Firefly',(math.cos(a)*(2.0+.5*(i%3)),math.sin(a)*1.4,2.0+.08*(i%4)),(.045,.045,.045),gold)
    f.keyframe_insert(data_path='location',frame=10500+i*5)
    f.location.z+=.35; f.keyframe_insert(data_path='location',frame=10800+i*5)

# Story-driven camera choreography: 10 acts, each with establishing, medium and close shots.
cam=bpy.data.objects.get('Cinematic Camera') or bpy.data.objects.get('Camera'); scene.camera=cam; cam.data.dof.use_dof=True
cam.data.dof.aperture_fstop=3.0
poses=[
(0,(9,-15,6.5),(0,0,2.1),52),(25,(4,-12,4.5),(0,0,2.3),58),(55,(-4,-10,3.7),(-.5,0,2.4),62),
(75,(5,-11,4.6),(0,-.5,2.4),55),(115,(1,-8,3.5),(0,-.8,1.2),70),(145,(7,-12,4.8),(0,0,2.3),52),
(185,(3,-9,4.0),(1,-1,1.9),60),(220,(-5,-10,4.4),(0,-.5,2.1),56),(260,(2,-7,3.4),(0,-.8,1.0),72),
(300,(-7,-12,5.0),(-1,0,2.1),50),(335,(7,-12,5.0),(1,-1,2.0),55),(375,(1,-13,4.2),(0,0,2.2),65),
(415,(-8,-10,5.3),(0,0,2.4),52),(455,(7,-12,5.0),(0,0,2.3),55),(490,(1,-11,3.7),(0,-.5,1.8),68),
(520,(-6,-10,5.2),(0,0,2.2),54),(550,(5,-13,5.6),(0,-.5,2.3),58),(580,(0,-14,4.8),(0,-.5,2.2),55),(600,(0,-15,4.8),(0,-.5,2.2),55)]
for p in poses:keycam(*p)
if cam.animation_data:
    for fc in cam.animation_data.action.fcurves:
        for q in fc.keyframe_points:q.interpolation='BEZIER'

# Milo/Pip movement and performance. Keep motion continuous between camera shots.
milo_parts=[o for o in bpy.context.scene.objects if o.name.startswith('Milo')]
for sec,x in [(0,-1),(75,-.2),(145,1),(220,0),(300,-2),(375,1.5),(455,0),(520,-.5),(580,0)]:
    f=int(sec*FPS)
    for o in milo_parts:
        if o.parent is None:
            o.location.x += x
            o.keyframe_insert(data_path='location',index=0,frame=f)
for sec,x in [(0,7),(145,4),(220,1.2),(300,1.0),(375,5.5),(455,1),(520,.2),(580,0)]:
    f=int(sec*FPS); root.location.x=x; root.keyframe_insert(data_path='location',index=0,frame=f); root.location.y=-4 if sec<220 else -1; root.keyframe_insert(data_path='location',index=1,frame=f)
# Natural breathing/bobbing and expressive head motion.
head=bpy.data.objects.get('Milo Head'); body=bpy.data.objects.get('Milo Body'); trunk=bpy.data.objects.get('Milo Trunk')
for f in range(1,END+1,12):
    t=f/FPS
    if body: body.location.z=.035*math.sin(t*5.0); body.keyframe_insert(data_path='location',index=2,frame=f)
    if head: head.rotation_euler[2]=math.radians(2.5)*math.sin(t*1.7); head.keyframe_insert(data_path='rotation_euler',index=2,frame=f)
    if trunk: trunk.rotation_euler[2]=math.radians(4)*math.sin(t*2.2); trunk.keyframe_insert(data_path='rotation_euler',index=2,frame=f)
# Magic seed rises into flower near finale.
for f,z in [(1,.50),(7200,.50),(10500,.52),(11200,1.0),(11800,1.55),(12400,1.9),(END,1.9)]:
    seed.location.z=z; seed.keyframe_insert(data_path='location',index=2,frame=f)
for f,s in [(1,.03),(11200,.03),(11800,.35),(12400,1.0),(END,1.0)]:
    flower.scale=(s,s,s); flower.keyframe_insert(data_path='scale',frame=f)

# Day-to-sunset lighting progression.
for l in [o for o in scene.objects if o.type=='LIGHT']:
    if l.data.type=='SUN':
        l.data.energy=1.8; l.data.keyframe_insert(data_path='energy',frame=1); l.data.energy=1.0; l.data.keyframe_insert(data_path='energy',frame=END)

# Windows built-in speech: no paid service required. Generate character/narrator dialogue locally.
lines=[(0,'NARRATOR','In a bright little meadow, where the grass danced in the morning breeze, lived a young elephant named Milo.'),(38,'MILO','Good morning, meadow! Today feels like a very special day.'),(72,'NARRATOR','That morning, Milo discovered a tiny golden seed glowing beneath a flower.'),(105,'MILO','Whoa... are you a little star hiding in the grass?'),(145,'PIP','Milo! What did you find?'),(165,'MILO','I do not know yet. But I think it needs our help.'),(205,'NARRATOR','Together, the friends planted the mysterious seed beside the pond.'),(250,'PIP','Maybe it will grow into something enormous!'),(275,'MILO','Whatever it becomes, we will take care of it together.'),(320,'NARRATOR','Then a playful gust of wind lifted the seed and carried it toward the old forest.'),(350,'MILO','Come on, Pip! We have to find it before it gets lost.'),(390,'PIP','I am right behind you!'),(430,'NARRATOR','Deep among the trees, tiny fireflies appeared, one by one, forming a sparkling trail.'),(465,'MILO','Look! They are showing us the way.'),(495,'NARRATOR','The friends followed the lights into a quiet clearing beneath the moon.'),(525,'PIP','There it is! Our little golden seed.'),(545,'MILO','Let us bring it home.'),(565,'NARRATOR','Together they returned to the meadow, planted the seed again, and waited.'),(585,'NARRATOR','By sunrise, a beautiful moonflower opened its petals. Milo and Pip smiled.'),(598,'MILO','Sometimes the smallest things grow when friends take care of them.')]

def speak(text,path,rate):
    safe=text.replace("'","''"); pp=path.replace("'","''")
    cmd="$ErrorActionPreference='SilentlyContinue'; Add-Type -AssemblyName System.Speech; $s=New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.Rate=%d; $s.Volume=100; $s.SetOutputToWaveFile('%s'); $s.Speak('%s'); $s.Dispose()"%(rate,pp,safe)
    subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-Command',cmd],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
for i,(sec,role,text) in enumerate(lines):
    p=os.path.join(AUDIO,'line_%02d.wav'%i)
    if not os.path.exists(p): speak(text,p,0 if role=='NARRATOR' else (3 if role=='MILO' else 7))

# Gentle original background music generated as a WAV so the project has complete audio.
music=os.path.join(AUDIO,'music.wav')
if not os.path.exists(music):
    sr=22050; chords=[261.63,329.63,392.0,349.23,293.66,392.0]; total=sr*600
    with wave.open(music,'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        for i in range(total):
            t=i/sr; n=chords[int(t/8)%len(chords)]; v=.055*math.sin(2*math.pi*n*t)+.022*math.sin(2*math.pi*n*2*t)+.012*math.sin(2*math.pi*n*3*t); env=min(1,t/3,(600-t)/3); w.writeframes(struct.pack('<h',int(v*32767*max(0,env))))

# Master sequencer: 3D scene + dialogue + music in one H.264/AAC deliverable.
master=bpy.data.scenes.get('MASTER') or bpy.data.scenes.new('MASTER')
if master.sequence_editor: master.sequence_editor_clear()
seq=master.sequence_editor_create(); ss=seq.sequences.new_scene('EPISODE 3D',scene,1,1); ss.frame_final_duration=END
ms=seq.sequences.new_sound('Original Music',music,2,1); ms.frame_final_duration=END; ms.volume=.45
for i,(sec,role,text) in enumerate(lines):
    p=os.path.join(AUDIO,'line_%02d.wav'%i)
    if os.path.exists(p):
        s=seq.sequences.new_sound(role+'_'+str(i),p,10+i,1+int(sec*FPS)); s.volume=1.0
master.frame_start=1; master.frame_end=END; master.render.engine='BLENDER_EEVEE_NEXT'; master.render.resolution_x=1920; master.render.resolution_y=1080; master.render.resolution_percentage=100; master.render.fps=FPS
master.render.image_settings.file_format='FFMPEG'; master.render.ffmpeg.format='MPEG4'; master.render.ffmpeg.codec='H264'; master.render.ffmpeg.constant_rate_factor='HIGH'; master.render.ffmpeg.audio_codec='AAC'; master.render.ffmpeg.audio_bitrate=192; master.render.filepath=os.path.join(OUT,'Milo_and_the_Moonflower_FINAL.mp4')
master.render.use_sequencer=True
bpy.context.window.scene=master
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'Milo_and_the_Moonflower_FINAL.blend'))
print('FULL PRODUCTION START:',master.render.filepath)
bpy.ops.render.render(animation=True)
print('FULL PRODUCTION COMPLETE:',master.render.filepath)
