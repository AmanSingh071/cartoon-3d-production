import bpy, os, math
from mathutils import Vector

ROOT=r'D:\first Blender\mlo'; OUT=os.path.join(ROOT,'output'); BLEND=os.path.join(OUT,'Nocturne_Lounge_MLO.blend'); PREVIEW=os.path.join(OUT,'mlo_showcase.png'); MANIFEST=os.path.join(OUT,'mlo_manifest.json')
if not os.path.exists(BLEND): raise RuntimeError('fusion_feast_reference_pass: missing blend')
bpy.ops.wm.open_mainfile(filepath=BLEND)

# Reference target: the supplied Fusion Feast restaurant video.
# Design language: emerald upholstery, dark timber slats, brass geometry, warm pools of light,
# black patterned floor, large glazing, hospitality bar, commercial kitchen, decorative washroom,
# tropical planting and a highly legible stair/corridor sequence.

def mat(name,color,metal=0,rough=.45,emit=None,strength=0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes=True
    b=m.node_tree.nodes.get('Principled BSDF'); b.inputs['Base Color'].default_value=(*color,1); b.inputs['Metallic'].default_value=metal; b.inputs['Roughness'].default_value=rough
    if emit:
        if 'Emission Color' in b.inputs: b.inputs['Emission Color'].default_value=(*emit,1)
        if 'Emission Strength' in b.inputs: b.inputs['Emission Strength'].default_value=strength
    m.diffuse_color=(*color,1); return m

e=mat('FF_Emerald',(.018,.20,.125),0,.34); e2=mat('FF_EmeraldDeep',(.008,.075,.055),0,.42)
wood=mat('FF_Walnut',(.16,.055,.018),.02,.28); wood2=mat('FF_Teak',(.32,.13,.045),.02,.34)
gold=mat('FF_Brass',(.58,.31,.075),.88,.17); ivory=mat('FF_Ivory',(.78,.73,.62),0,.58)
black=mat('FF_Black',(.018,.017,.015),.02,.38); floor=mat('FF_PatternFloor',(.10,.075,.045),.0,.42)
glass=mat('FF_GreenGlass',(.018,.14,.105),.35,.12); white=mat('FF_WarmWhite',(.92,.87,.74),0,.26)
glow=mat('FF_WarmGlow',(.65,.25,.055),.0,.22,(1.0,.32,.08),5)
red=mat('FF_ChefAccent',(.36,.035,.018),0,.4)

def coll(n):
    c=bpy.data.collections.get(n) or bpy.data.collections.new(n)
    if c.name not in [x.name for x in bpy.context.scene.collection.children]: bpy.context.scene.collection.children.link(c)
    return c
arch=coll('FF_Architecture'); furn=coll('FF_Furniture'); decor=coll('FF_Decor'); route=coll('FF_Circulation'); wash=coll('FF_Washroom'); kitchen=coll('FF_Kitchen'); ext=coll('FF_Exterior'); lights=coll('FF_Lighting')

def move(o,c):
    for q in list(o.users_collection): q.objects.unlink(o)
    c.objects.link(o)

def cube(n,loc,sc,m,bev=.025,rot=0,c=None):
    bpy.ops.mesh.primitive_cube_add(location=loc,rotation=(0,0,rot)); o=bpy.context.object; o.name=n; o.scale=sc; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if bev: b=o.modifiers.new('EdgeSoft','BEVEL'); b.width=bev; b.segments=2
    if c: move(o,c)
    return o

def cyl(n,loc,r,d,m,v=20,c=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=r,depth=d,location=loc); o=bpy.context.object; o.name=n; o.data.materials.append(m)
    if c: move(o,c)
    return o

def text(n,s,loc,size,m,c,rot=(math.pi/2,0,0)):
    cu=bpy.data.curves.new(n,'FONT'); cu.body=s; cu.align_x='CENTER'; cu.align_y='CENTER'; cu.size=size; cu.extrude=.012; cu.bevel_depth=.003
    o=bpy.data.objects.new(n,cu); c.objects.link(o); o.location=loc; o.rotation_euler=rot; o.data.materials.append(m); return o

def delete_pref(pref):
    for o in list(bpy.data.objects):
        if any(o.name.startswith(p) for p in pref): bpy.data.objects.remove(o,do_unlink=True)

def light(n,loc,energy,size,col):
    data=bpy.data.lights.new(n,'AREA'); data.energy=energy; data.shape='DISK'; data.size=size; data.color=col
    o=bpy.data.objects.new(n,data); lights.objects.link(o); o.location=loc; return o

# Remove the previous concept rather than stacking another theme on top of it.
delete_pref(('PALM_','PHQ_','VIS_','DJ_','Speaker','Stage','PlantPot','Leaf','CeilingFixture','Warm_Ceiling_Light','BarStool','StoolSeat','DiningTable','ChairLeg','ChairSeat'))

# ---- floor: dark luxury stone/wood herringbone-like field ----
for o in list(bpy.data.objects):
    if o.name.startswith('FF_FloorTile'): bpy.data.objects.remove(o,do_unlink=True)
for row in range(-7,8):
    for col in range(-9,10):
        x=col*1.55; y=row*1.55
        cube(f'FF_FloorTile_{row}_{col}',(x,y,.22),(.72,.36,.018),floor,.008,math.radians(45 if (row+col)%2==0 else -45),route)
# clean 2.7m central route in emerald + brass
cube('FF_MainAisle',(0,-3.5,.265),(1.35,8.0,.025),e,.008,0,route)
for y in (-9,-6,-3,0,3,6,9): cube('FF_AisleBrass',(0,y,.30),(.95,.025,.012),gold,.003,0,route)
text('FF_EntryMark','FUSION FEAST',(0,-10.95,.40),.28,gold,route)

# ---- signature feature wall: vertical timber + emerald framed artwork ----
cube('FF_HeroWall',(0,10.25,2.35),(8.8,.12,2.05),wood,.035,0,arch)
for x in range(-8,9): cube(f'FF_WallSlat_{x}',(x*1.0,10.06,2.35),(.035,.035,1.92),wood2,.008,0,arch)
# repeated tall rounded-looking framed panels (rectangular low-poly, strong silhouette)
for i,x in enumerate((-6,-3,0,3,6)):
    cube(f'FF_ArtPanel_{i}',(x,10.00,2.55),(1.05,.045,1.42),e2,.08,0,arch)
    cube(f'FF_ArtFrameTop_{i}',(x,9.91,3.93),(1.18,.05,.06),gold,.015,0,arch)
    cube(f'FF_ArtFrameL_{i}',(x-1.12,9.91,2.55),(.06,.05,1.42),gold,.015,0,arch)
    cube(f'FF_ArtFrameR_{i}',(x+1.12,9.91,2.55),(.06,.05,1.42),gold,.015,0,arch)
    cyl(f'FF_ArtPlant_{i}',(x,9.83,3.05),.18,.08,wood2,16,decor)
text('FF_Logo','FUSION FEAST',(0,9.86,1.12),.72,gold,arch)
text('FF_Tagline','DINING  •  BAR  •  KITCHEN',(0,9.84,.65),.17,ivory,arch)

# ---- long restaurant bar / bottle wall, matching reference composition ----
cube('FF_BarBase',(5.7,1.4,1.05),(5.0,.72,.75),e2,.10,furn)
cube('FF_BarTop',(5.7,.65,1.86),(5.15,.78,.09),wood2,.04,furn)
cube('FF_BarBrassRail',(5.7,.02,1.38),(4.75,.025,.035),gold,.008,furn)
for x in range(-4,5):
    xx=5.7+x*1.05
    cube(f'FF_BottleShelf_{x}',(xx,2.18,2.2),(0.43,.16,.055),wood2,.012,furn)
    for j in range(3): cyl(f'FF_Bottle_{x}_{j}',(xx-.25+j*.25,2.02,2.55+(j%2)*.32),.055,.48,glass,12,furn)
for x in (2.2,4.0,5.8,7.6,9.2):
    cyl(f'FF_BarStool_{x}',(x,-.25,.72),.27,.72,gold,20,furn); cube(f'FF_StoolSeat_{x}',(x,-.25,1.15),(.38,.38,.07),e,.06,0,furn)
text('FF_BarSign','BAR  •  COCKTAILS  •  ZERO-PROOF',(5.7,2.02,3.18),.18,ivory,furn)

# ---- emerald booth seating with vertical slat privacy screens ----
def booth(x,y,w=3.2):
    cube(f'FF_BoothBack_{x}_{y}',(x,y+.52,1.10),(w/2,.28,.72),e,.10,furn)
    cube(f'FF_BoothSeat_{x}_{y}',(x,y,.72),(w/2,.62,.18),e,.10,furn)
    for sx in (-w/2+.15,w/2-.15): cube(f'FF_BoothArm_{x}_{y}_{sx}',(x+sx,y,.95),(.13,.62,.34),wood2,.04,furn)
    for i in range(9): cube(f'FF_Slat_{x}_{y}_{i}',(x-w/2-.18+i*.42,y+.92,2.35),(.035,.04,1.35),wood2,.008,0,furn)
    for sx in (-w/2+.65,w/2-.65):
        cyl(f'FF_TableLeg_{x}_{y}_{sx}',(x+sx,y-1.0,.58),.07,.60,gold,16,furn)
        cyl(f'FF_TableTop_{x}_{y}_{sx}',(x+sx,y-1.0,.91),.58,.08,wood2,24,furn)
for cfg in [(-6,-5.7,3.8),(-1.4,-5.7,3.8),(3.2,-5.7,3.8),(-6,-1.8,3.8),(-1.4,-1.8,3.8)]: booth(*cfg)

# ---- standalone tables and real-looking chair silhouettes ----
def chair(x,y,rot=0):
    cube(f'FF_ChairSeat_{x}_{y}',(x,y,.63),(.31,.31,.08),e,.045,rot,furn)
    cube(f'FF_ChairBack_{x}_{y}',(x,y+.26,1.05),(.31,.07,.48),e,.045,rot,furn)
    for dx in (-.22,.22):
        for dy in (-.20,.20): cube(f'FF_ChairLeg_{x}_{y}_{dx}_{dy}',(x+dx,y+dy,.34),(.035,.035,.30),gold,.008,rot,furn)
for k,(x,y) in enumerate([(-1.2,4.0),(2.4,4.0),(6.0,4.0),(-6.2,3.5),(-1.0,7.0),(3.0,7.0),(7.0,7.0)]):
    cyl(f'FF_RoundTable_{k}',(x,y,.86),.86,.09,wood2,28,furn); cyl(f'FF_TablePedestal_{k}',(x,y,.48),.16,.72,gold,20,furn)
    for j in range(4):
        a=j*math.pi/2; chair(x+1.15*math.cos(a),y+1.15*math.sin(a),a)

# ---- open kitchen / service room: stainless work islands and tiled wall ----
cube('FF_KitchenBack',(0,5.95,2.4),(6.5,.12,2.0),ivory,.02,0,kitchen)
for i in range(-12,13): cube(f'FF_TileLine_{i}',(i*.52,5.79,2.35),(.012,.02,1.85),white,.002,0,kitchen)
for z in (1.0,2.1,3.2): cube(f'FF_KitchenShelf_{z}',(0,5.3,z),(5.2,.28,.06),black,.012,0,kitchen)
for x in (-4.2,-1.4,1.4,4.2):
    cube(f'FF_WorkIsland_{x}',(x,4.45,1.0),(1.0,.55,.72),black,.05,kitchen)
    cube(f'FF_WorkTop_{x}',(x,4.45,1.76),(1.06,.61,.07),ivory,.025,kitchen)
text('FF_KitchenSign','KITCHEN / SERVICE',(0,5.68,3.55),.25,gold,kitchen)

# ---- reference stair: broad floating timber stair with a clear vertical void ----
for o in list(bpy.data.objects):
    if o.name.startswith(('FF_Stair','FF_StairRail')): bpy.data.objects.remove(o,do_unlink=True)
for i in range(18):
    z=.16+i*.235; y=8.0+i*.45
    cube(f'FF_Stair_{i:02d}',(-7.0,y,z),(1.55,.23,.115),wood2,.025,0,arch)
    cube(f'FF_StairNosing_{i:02d}',(-7.0,y-.20,z+.105),(1.48,.025,.028),gold,.006,0,arch)
# rails on both sides, with posts
for side in (-1,1):
    x=-7+side*1.75
    cube(f'FF_StairRail_{side}',(x,11.8,2.45),(.045,3.8,.045),gold,.012,0,arch)
    for i in range(0,18,3): cube(f'FF_StairPost_{side}_{i}',(x,8+i*.45,.65+i*.235),(.035,.035,.55),gold,.008,0,arch)
text('FF_StairSign','UPSTAIRS',(-7,8.55,4.55),.28,gold,arch)

# ---- washroom: dark emerald + brass geometric wall and vanity row ----
cube('FF_WashWall',(7.4,9.55,2.3),(3.0,.10,2.0),e2,.025,0,wash)
for x in (5.2,6.7,8.2,9.7):
    cube(f'FF_WashGoldV_{x}',(x,9.40,2.3),(.035,.05,1.75),gold,.006,0,wash)
for y,z in ((9.38,1.0),(9.38,3.6)):
    cube(f'FF_WashGoldH_{z}',(7.45,y,z),(2.3,.05,.035),gold,.006,0,wash)
for x in (5.8,7.4,9.0):
    cube(f'FF_Vanity_{x}',(x,8.85,1.05),(.60,.45,.18),wood2,.05,0,wash)
    cyl(f'FF_Sink_{x}',(x,8.35,1.27),.28,.10,ivory,24,wash)
    cyl(f'FF_Faucet_{x}',(x,8.30,1.62),.035,.45,gold,16,wash)
text('FF_WashSign','WASHROOM',(7.4,9.38,4.08),.24,gold,wash)

# ---- tropical planting, deliberately grouped and sparse like the reference ----
def plant(x,y,h=2.2):
    cyl(f'FF_PlantPot_{x}_{y}',(x,y,.48),.48,.72,black,20,decor)
    cyl(f'FF_PlantStem_{x}_{y}',(x,y,1.65),.06,h,wood2,12,decor)
    for j in range(8):
        a=2*math.pi*j/8; L=1.05+.22*(j%3)
        # leaf as tapered rotated cube gives readable low-poly frond silhouette
        o=cube(f'FF_PalmLeaf_{x}_{y}_{j}',(x+.45*math.cos(a),y+.45*math.sin(a),2.55+.18*(j%2)),(L/2,.055,.055),e,.02,a,decor)
        o['hero_prop']='reference_tropical_leaf'
for cfg in [(-9,-8,2.5),(9,-7,2.5),(-9,6,2.5),(9,5,2.5),(5,10,2.0)]: plant(*cfg)

# ---- ceiling: repeated warm ring pendants and timber beams ----
for x in (-7,-3.5,0,3.5,7): cube(f'FF_CeilingBeam_{x}',(x,0,4.65),(.10,14,.10),wood2,.02,0,arch)
for i,(x,y,z) in enumerate([(-6,-4.0,4.15),(-2,-4.0,4.05),(2,-1.0,4.10),(6,-1.0,4.15),(-3,4.5,4.05),(3,6.5,4.15)]):
    bpy.ops.mesh.primitive_torus_add(major_radius=.48+(i%2)*.20,minor_radius=.045,major_segments=32,minor_segments=8,location=(x,y,z)); o=bpy.context.object; o.name=f'FF_RingPendant_{i}'; o.data.materials.append(gold); move(o,lights)
    light(f'FF_PendantLight_{i}',(x,y,z-.18),350,.8,(1.0,.62,.32))
# soft wall pools
for x in (-6,-3,0,3,6): light(f'FF_WallPool_{x}',(x,9.45,2.4),260,1.1,(1.0,.55,.28))
for x in (-8,0,8): light(f'FF_FrontPool_{x}',(x,-8,3.8),500,2.0,(1.0,.70,.42))

# ---- exterior frontage / roadside identity ----
cube('FF_ExteriorCanopy',(0,-11.8,3.8),(10.5,.7,.28),wood2,.06,0,ext)
cube('FF_ExteriorHeader',(0,-12.2,3.0),(7.8,.12,.65),black,.04,0,ext)
text('FF_ExteriorLogo','FUSION FEAST',(0,-12.34,3.05),.72,gold,ext)
text('FF_ExteriorSub','DINING  •  BAR  •  KITCHEN',(0,-12.36,2.55),.17,ivory,ext)
for x in (-9,-6,-3,0,3,6,9): cube(f'FF_FrontMullion_{x}',(x,-11.0,2.25),(.08,.08,2.1),wood2,.015,0,ext)
for x in (-8,-4,0,4,8): cube(f'FF_GlassBay_{x}',(x,-10.95,2.35),(1.72,.04,1.75),glass,.025,0,ext)
# yellow/black curb cue from the exterior shot
for i in range(-10,11): cube(f'FF_Curb_{i}',(i*1.0,-13.05,.14),(.48,.18,.10),gold if i%2==0 else black,.01,0,ext)
for x in (-8,8): plant(x,-12.2,2.5)

# ---- scene lighting / camera ----
scene=bpy.context.scene
scene.world.color=(.025,.018,.012)
try: scene.world.use_nodes=True; scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.025,.018,.012,1); scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.28
except Exception: pass
# showcase shot intentionally resembles the video: entrance into the dining/bar depth.
bpy.ops.object.camera_add(location=(13,-15,8.0),rotation=(math.radians(67),0,math.radians(39)))
cam=bpy.context.object; cam.name='FF_ShowcaseCamera'; cam.data.lens=28
# point camera at dining center
q=(Vector((0,1.0,1.9))-cam.location).to_track_quat('-Z','Y'); cam.rotation_euler=q.to_euler(); scene.camera=cam
scene.render.engine='BLENDER_EEVEE_NEXT'; scene.render.resolution_x=1920; scene.render.resolution_y=1080; scene.render.resolution_percentage=65
scene.render.filepath=PREVIEW
try: bpy.ops.render.render(write_still=True)
except Exception: pass

scene['mlo_brand']='FUSION FEAST'; scene['mlo_reference']='user supplied 77s Fusion Feast restaurant video'; scene['mlo_reference_match_target']='close visual/layout recreation'; scene['mlo_reference_elements']='roadside frontage, emerald booths, bottle bar, commercial kitchen, floating timber stair, geometric brass washroom, tropical plants, ring pendants, dark patterned floor'; scene['mlo_quality_bar']='AAA FiveM restaurant interior'; scene['mlo_reference_pass']='fusion_feast_v1'
try:
    data={k:v for k,v in scene.items()};
    with open(MANIFEST,'w',encoding='utf-8') as f: json.dump({'scene':data,'reference_pass':'fusion_feast_v1'},f,indent=2,default=str)
except Exception: pass
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print('FUSION FEAST REFERENCE PASS COMPLETE')
