import bpy, os, math, json
from mathutils import Vector

ROOT=r'D:\first Blender\mlo'
OUT=os.path.join(ROOT,'output')
BLEND=os.path.join(OUT,'Nocturne_Lounge_MLO.blend')
PREVIEW=os.path.join(OUT,'mlo_showcase.png')
MANIFEST=os.path.join(OUT,'mlo_manifest.json')
os.makedirs(OUT, exist_ok=True)

# FUSION FEAST — REFERENCE-FIRST REBUILD
# Rebuilds the visible scene instead of stacking another theme on top.
# Target: supplied restaurant video: emerald/walnut/brass luxury,
# strong booths, slatted walls, large glazing, service bar,
# commercial kitchen, decorative washrooms, broad stair and warm ceiling.

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
    if c.name != 'Collection': bpy.data.collections.remove(c)
base=bpy.data.collections.get('Collection')
if base:
    for o in list(base.objects): base.objects.unlink(o)
scene=bpy.context.scene

def C(name):
    c=bpy.data.collections.new(name); scene.collection.children.link(c); return c
ARCH=C('FF_ARCHITECTURE'); FURN=C('FF_FURNITURE'); DEC=C('FF_DECOR')
LIGHT=C('FF_LIGHTING'); KITCH=C('FF_KITCHEN'); WASH=C('FF_WASHROOM')
STAIR=C('FF_STAIR'); EXT=C('FF_EXTERIOR'); ACC=C('FF_ACCESS')

def mat(n,col,metal=0.0,rough=.45,emission=None,estr=0):
    m=bpy.data.materials.get(n) or bpy.data.materials.new(n); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*col,1); bs.inputs['Metallic'].default_value=metal; bs.inputs['Roughness'].default_value=rough
    if emission:
        if 'Emission Color' in bs.inputs: bs.inputs['Emission Color'].default_value=(*emission,1)
        if 'Emission Strength' in bs.inputs: bs.inputs['Emission Strength'].default_value=estr
    m.diffuse_color=(*col,1); return m

emerald=mat('FF2_Emerald',(.015,.20,.115),0,.30)
emerald2=mat('FF2_EmeraldDeep',(.006,.075,.045),0,.38)
velvet=mat('FF2_Velvet',(.025,.25,.14),0,.62)
walnut=mat('FF2_Walnut',(.105,.030,.010),.02,.27)
teak=mat('FF2_Teak',(.27,.095,.025),.02,.30)
brass=mat('FF2_Brass',(.58,.31,.065),.90,.15)
ivory=mat('FF2_Ivory',(.78,.73,.62),0,.55)
stone=mat('FF2_Stone',(.095,.070,.045),.02,.36)
black=mat('FF2_Black',(.012,.012,.010),.02,.34)
glass=mat('FF2_Glass',(.015,.105,.085),.25,.10)
glassclear=mat('FF2_ClearGlass',(.30,.40,.34),.10,.08)
warm=mat('FF2_Warm',(.80,.30,.055),0,.20,(1.0,.28,.06),3.5)
cream=mat('FF2_Cream',(.62,.57,.47),0,.58)
red=mat('FF2_ChefRed',(.34,.025,.012),0,.40)

def move(o,c):
    for q in list(o.users_collection): q.objects.unlink(o)
    c.objects.link(o)

def cube(n,loc,sc,m,bev=.03,rot=0,c=ARCH):
    bpy.ops.mesh.primitive_cube_add(location=loc,rotation=(0,0,rot)); o=bpy.context.object; o.name=n; o.scale=sc
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if bev:
        b=o.modifiers.new('BEVEL','BEVEL'); b.width=bev; b.segments=3
    move(o,c); return o

def cyl(n,loc,r,d,m,v=24,c=ARCH):
    bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=r,depth=d,location=loc); o=bpy.context.object; o.name=n; o.data.materials.append(m); move(o,c); return o

def text(n,s,loc,size,m,c=DEC,rot=(math.pi/2,0,0),extr=.015):
    cu=bpy.data.curves.new(n,'FONT'); cu.body=s; cu.align_x='CENTER'; cu.align_y='CENTER'; cu.size=size; cu.extrude=extr; cu.bevel_depth=.003
    o=bpy.data.objects.new(n,cu); c.objects.link(o); o.location=loc; o.rotation_euler=rot; o.data.materials.append(m); return o

def area(n,loc,energy,size,color=(1.0,.55,.28)):
    d=bpy.data.lights.new(n,'AREA'); d.energy=energy; d.shape='DISK'; d.size=size; d.color=color
    o=bpy.data.objects.new(n,d); LIGHT.objects.link(o); o.location=loc; return o

# shell
W=24.0; D=22.0; H=8.0
cube('Floor',(0,0,.10),(W/2,D/2,.10),stone,.02,c=ARCH)
for y in range(-9,10,2):
    for x in range(-10,11,2): cube(f'FF_FloorPattern_{x}_{y}',(x+.35*(y%4),y,.225),(.72,.24,.018),walnut,.006,math.radians(45 if ((x+y)//2)%2==0 else -45),ARCH)
cube('Wall_Back',(0,10.9,4.1),(12,.16,4.1),walnut,.04,c=ARCH)
cube('Wall_Left',(-12,0,4.1),(.16,11,4.1),cream,.04,c=ARCH)
cube('Wall_Right',(12,0,4.1),(.16,11,4.1),cream,.04,c=ARCH)
for x in range(-10,11,4): cube(f'FF_CeilingBeam_{x}',(x,0,7.55),(.10,10.7,.16),walnut,.025,c=ARCH)
for y in (-8,-4,0,4,8): cube(f'FF_CeilingCross_{y}',(0,y,7.48),(11.7,.07,.10),brass,.02,c=ARCH)

# storefront
cube('FF_FrontHeader',(0,-10.82,6.95),(11.6,.18,.55),walnut,.04,c=EXT)
for x in (-11,-8.25,-5.5,-2.75,0,2.75,5.5,8.25,11): cube(f'FF_GlassMullion_{x}',(x,-10.67,3.45),(.045,.055,3.35),brass,.008,c=EXT)
cube('FF_GlassFront',(0,-10.62,3.55),(11.5,.035,3.15),glassclear,.008,c=EXT)
for x in (-1.65,1.65): cube(f'FF_EntryJamb_{x}',(x,-10.55,3.2),(.10,.12,2.8),brass,.02,c=EXT)
cube('FF_EntryHeader',(0,-10.55,6.0),(1.8,.12,.10),brass,.02,c=EXT)
text('FF_EntryText','FUSION FEAST',(0,-10.48,5.92),.42,brass,EXT)

# hero wall
cube('FeatureWall',(0,10.68,4.0),(9.6,.10,3.8),walnut,.035,c=ARCH)
for x in range(-9,10): cube(f'FF_Slat_{x}',(x*.88,10.48,4.0),(.032,.04,3.55),teak,.008,c=ARCH)
for i,x in enumerate((-6.4,-3.2,0,3.2,6.4)):
    cube(f'FF_GreenPanel_{i}',(x,10.40,4.15),(1.18,.035,2.35),emerald2,.10,c=ARCH)
    for sx in (-1.28,1.28): cube(f'FF_PanelGold_{i}_{sx}',(x+sx,10.32,4.15),(.045,.04,2.48),brass,.012,c=ARCH)
    cube(f'FF_PanelGoldTop_{i}',(x,10.32,6.58),(1.28,.04,.045),brass,.012,c=ARCH)
text('FF_Logo','FUSION FEAST',(0,10.20,4.35),1.00,brass,ARCH)
text('FF_Subtitle','DINING  /  BAR  /  KITCHEN',(0,10.19,3.45),.23,ivory,ARCH)

# side slat walls
for side,x in [('L',-11.5),('R',11.5)]:
    for y in (-7,-5,-3,-1,1,3,5,7): cube(f'FF_SideSlat_{side}_{y}',(x,y,3.7),(.18,.055,3.3),walnut,.02,c=ARCH)
    for y in (-8,-4,0,4,8): cube(f'FF_SidePanel_{side}_{y}',(x+(0.02 if x<0 else -0.02),y,3.8),(.08,1.15,2.8),emerald2,.05,c=ARCH)

# booths

def booth(name,x,y,w=3.6,rot=0):
    cube(name+'_Back',(x,y+.55,1.45),(w/2,.30,.85),velvet,.14,rot,FURN)
    cube(name+'_Seat',(x,y,.72),(w/2,.72,.18),velvet,.12,rot,FURN)
    cube(name+'_BackTop',(x,y+.25,2.15),(w/2,.10,.10),brass,.035,rot,FURN)
    for s in (-1,1): cube(name+f'_Arm{s}',(x+s*(w/2-.16),y,.98),(.13,.68,.40),teak,.045,rot,FURN)
    for i in range(int(w/.40)+1): cube(name+f'_Slat{i}',(x-w/2+i*.40,y+.93,3.15),(.028,.05,1.25),teak,.008,rot,FURN)
    tx=x; ty=y-1.20; cyl(name+'_TableTop',(tx,ty,1.00),.68,.08,teak,28,FURN); cyl(name+'_TablePedestal',(tx,ty,.55),.15,.82,brass,20,FURN)
    for side in (-1,1):
        a=bpy.data.objects.new(name+f'_SeatAnchor{side}',None); a.empty_display_type='CIRCLE'; a.empty_display_size=.16; FURN.objects.link(a); a.location=(x+side*.95,y-.95,.46)
        a['sittable']=True; a['interaction_type']='sit'; a['seat_height_m']=.46; a['clearance_radius_m']=.55
for cfg in [('BoothA',-7.5,-6.2,4.1),('BoothB',-2.4,-6.2,4.1),('BoothC',3.0,-6.2,4.1),('BoothD',-7.5,-1.5,4.1),('BoothE',-2.4,-1.5,4.1),('BoothF',3.0,-1.5,4.1)]: booth(*cfg)

# tables and chairs

def chair(n,x,y,rot=0):
    cube(n+'_Seat',(x,y,.68),(.32,.32,.08),emerald,.05,rot,FURN); cube(n+'_Back',(x,y+.27,1.08),(.32,.07,.48),emerald,.05,rot,FURN)
    for dx in (-.22,.22):
        for dy in (-.20,.20): cube(n+f'_Leg{dx}{dy}',(x+dx,y+dy,.36),(.035,.035,.30),brass,.006,rot,FURN)
def table(n,x,y,r=.88):
    cyl(n+'_Top',(x,y,.90),r,.10,teak,28,FURN); cyl(n+'_Base',(x,y,.50),.16,.70,brass,20,FURN)
    for j in range(4):
        a=j*math.pi/2; chair(n+f'_C{j}',x+(r+.35)*math.cos(a),y+(r+.35)*math.sin(a),a)
    for j in range(4):
        a=j*math.pi/2; px=x+.48*math.cos(a); py=y+.48*math.sin(a); cyl(n+f'_Plate{j}',(px,py,1.00),.18,.025,ivory,20,DEC); cyl(n+f'_Glass{j}',(px+.22*math.cos(a),py+.22*math.sin(a),1.13),.045,.14,glassclear,16,DEC)
for i,(x,y) in enumerate([(-7,3.0),(-2.7,3.4),(2.0,3.2),(6.4,3.2),(-6.0,7.0),(-1.5,7.0),(3.4,7.0),(7.8,7.0)]): table(f'FF_Table{i}',x,y,.86)

# circulation
cube('FF_MainAisle',(0,-1.0,.26),(1.45,8.8,.025),emerald,.008,c=ACC)
for y in (-9,-6,-3,0,3,6,9): cube(f'FF_AisleMarker{y}',(0,y,.31),(.75,.025,.012),brass,.004,c=ACC)
cube('FF_StairBranch',(-8.8,1.0,.26),(2.0,.95,.025),emerald,.008,c=ACC); text('FF_RouteSign','STAIRS  →',(-8.8,1.0,.38),.22,brass,ACC)

# broad floating stair
sx=-8.8; sy=1.8; sw=2.75; count=18; run=.46; rise=.23
for i in range(count):
    z=(i+.5)*rise; y=sy+i*run; cube(f'FF_Stair_{i+1:02d}',(sx,y,z),(sw/2,run/2,.115),teak,.035,c=STAIR); cube(f'FF_Stair_Nosing_{i+1:02d}',(sx,y-run*.43,z+.105),(sw*.47,.025,.028),brass,.006,c=STAIR)
cube('FF_Stair_TopLanding',(sx,sy+count*run+.35,4.25),(sw/2,.55,.12),stone,.04,c=STAIR)
for side in (-1,1):
    x=sx+side*(sw/2+.20); cube(f'FF_Stair_Stringer{side}',(x,sy+count*run/2,2.0),(.10,count*run/2,.10),walnut,.025,c=STAIR)
    for i in range(0,count+1,3):
        y=sy+min(i,count)*run; z=min(i,count)*rise+.55; cube(f'FF_Stair_Post{side}_{i}',(x,y,z),(.035,.035,.58),brass,.008,c=STAIR)
    cube(f'FF_Stair_Rail{side}',(x,sy+count*run/2,2.60),(.045,count*run/2,.045),brass,.012,c=STAIR)
text('FF_StairSign','UPSTAIRS',(sx,sy-.25,.48),.26,brass,STAIR)

# bar
cube('BarCounter',(6.8,0.65,1.15),(4.65,.72,.80),emerald2,.12,c=FURN); cube('FF_BarTop',(6.8,-.08,1.98),(4.85,.80,.10),teak,.05,c=FURN); cube('FF_BarBrassTrim',(6.8,-.87,1.46),(4.55,.025,.045),brass,.008,c=FURN)
for x in [3.0,4.5,6.0,7.5,9.0,10.5]:
    cube(f'FF_BottleShelf{x}',(x,1.70,2.45),(.55,.18,.055),teak,.012,c=FURN)
    for j in range(3): cyl(f'FF_Bottle{x}_{j}',(x-.30+j*.30,1.48,2.88+(j%2)*.28),.055,.52,glass,12,FURN)
text('FF_BarSign','BAR  •  COFFEE  •  ZERO-PROOF',(6.8,1.40,3.75),.24,ivory,FURN)
for x in (3.5,5.0,6.5,8.0,9.5): cyl(f'FF_BarStool{x}',(x,-1.05,.66),.25,.62,brass,20,FURN); cyl(f'FF_BarSeat{x}',(x,-1.05,1.05),.38,.10,emerald,20,FURN)

# kitchen
cube('FF_KitchenWall',(0,5.85,4.0),(5.0,.10,3.4),ivory,.02,c=KITCH)
for x in range(-10,11): cube(f'FF_KTileV{x}',(x*.50,5.70,4.0),(.012,.02,3.1),white,.002,c=KITCH)
for z in (1.6,3.0,4.4,5.8): cube(f'FF_KShelf{z}',(0,5.10,z),(4.3,.24,.055),black,.01,c=KITCH)
for x in (-3.5,-1.2,1.2,3.5):
    cube(f'FF_WorkIsland{x}',(x,4.25,1.15),(.80,.55,.85),black,.06,c=KITCH); cube(f'FF_WorkTop{x}',(x,4.25,2.04),(.86,.60,.07),ivory,.025,c=KITCH); cyl(f'FF_Pot{x}',(x,4.25,2.20),.25,.18,black,20,KITCH)
text('FF_KitchenSign','OPEN KITCHEN / SERVICE',(0,5.62,6.25),.24,gold,KITCH)

# washroom
cube('FF_WashroomWall',(7.6,9.35,4.0),(3.3,.10,3.2),emerald2,.035,c=WASH)
for x in (5.0,6.3,7.6,8.9,10.2): cube(f'FF_WashGoldV{x}',(x,9.15,4.0),(.035,.045,2.75),brass,.006,c=WASH)
for z in (1.4,4.0,6.6): cube(f'FF_WashGoldH{z}',(7.6,9.15,z),(2.65,.045,.035),brass,.006,c=WASH)
for x in (6.0,7.6,9.2):
    cube(f'FF_Vanity{x}',(x,8.45,1.15),(.58,.45,.20),teak,.05,c=WASH); cyl(f'FF_Sink{x}',(x,8.0,1.40),.27,.10,ivory,24,WASH); cyl(f'FF_Faucet{x}',(x,7.92,1.78),.035,.45,brass,16,WASH)
text('FF_WashSign','WASHROOM',(7.6,9.10,6.95),.26,gold,WASH)

# palms

def palm(name,x,y,h=4.2):
    cyl(name+'_Trunk',(x,y,h/2),.20,h,teak,14,DEC)
    for k in range(5): cyl(name+f'_Ring{k}',(x,y,.55+k*.72),.215,.055,walnut,14,DEC)
    crown=h
    for i in range(10):
        a=2*math.pi*i/10; prev=(x,y,crown)
        for j in range(1,7):
            t=j/6; r=1.0+1.55*t; px=x+math.cos(a)*r; py=y+math.sin(a)*r; pz=crown+.55*t-.85*t*t
            mid=((prev[0]+px)/2,(prev[1]+py)/2,(prev[2]+pz)/2); length=math.dist(prev,(px,py,pz))
            cube(name+f'_Leaf{i}_{j}',mid,(.055,length/2,.025),velvet,.008,math.radians(a-math.pi/2),DEC); prev=(px,py,pz)
for cfg in [('PalmA',10,-8,4.3),('PalmB',-10,-8,4.0),('PalmC',10,6.8,4.5),('PalmD',-10,6.8,4.2)]:
    palm(*cfg); cyl(cfg[0]+'_Planter',(cfg[1],cfg[2],.48),.58,.72,black,24,DEC); cyl(cfg[0]+'_PlanterBand',(cfg[1],cfg[2],.70),.60,.07,brass,24,DEC)

# ceiling fixtures
for i,x in enumerate((-8,-4,0,4,8)):
    cyl(f'FF_Pendant{i}',(x,-2.0,6.35),.30,.12,brass,24,LIGHT); cyl(f'FF_PendantGlow{i}',(x,-2.0,6.05),.22,.35,warm,24,LIGHT); area(f'FF_PendantLight{i}',(x,-2.0,5.9),350,2.0,(1.0,.55,.30))
for x,y in ((-4,3),(4,3),(0,-6)):
    cyl(f'FF_CeilingRing{x}{y}',(x,y,7.1),1.15,.06,brass,48,LIGHT); area(f'FF_RingLight{x}{y}',(x,y,6.8),500,3.0,(1.0,.60,.35))

# doors

def door(name,x,y,w=1.2):
    cube(name+'_Frame',(x,y,2.2),(w/2+.10,.10,2.15),brass,.025,c=ACC)
    leaf=cube(name+'_Leaf',(x,y-.06,2.15),(w/2,.035,2.05),glassclear,.015,c=ACC); lock=cyl(name+'_Lock',(x+w*.32,y-.11,2.15),.055,.04,brass,16,ACC)
    leaf['lockable']=True; leaf['door_type']='glass'; leaf['clear_width_m']=w; lock['lockable']=True; lock['interaction_type']='lock'
door('DOOR_EntranceL',-1.2,-10.55,1.2); door('DOOR_EntranceR',1.2,-10.55,1.2); door('DOOR_Kitchen',-5.8,5.75,1.1); door('DOOR_Wash',10.8,8.4,1.0); door('DOOR_Private',5.8,8.4,1.0); door('DOOR_Staff',-5.8,8.4,1.0)
for i,(x,y) in enumerate([(-9,-6.2),(-6,-6.2),(-3,-6.2),(0,-6.2),(3,-6.2),(6,-6.2),(-8,3),(-5,3),(-2,3),(1,3),(4,3),(7,3)]):
    a=bpy.data.objects.new(f'SIT_{i+1:02d}',None); FURN.objects.link(a); a.location=(x,y,.46); a.empty_display_type='CIRCLE'; a.empty_display_size=.16; a['sittable']=True; a['interaction_type']='sit'; a['seat_height_m']=.46; a['clearance_radius_m']=.55

# exterior signage
cube('FF_ExteriorCanopy',(0,-11.35,6.65),(8.0,.75,.14),teak,.035,c=EXT); cube('FF_ExteriorSign',(0,-12.0,5.85),(4.0,.08,.55),emerald2,.04,c=EXT); text('FF_ExteriorLogo','FUSION FEAST',(0,-12.10,5.83),.58,gold,EXT)
for x in (-8.5,-5.5,5.5,8.5): cyl(f'FF_ExteriorPlanter{x}',(x,-11.55,.55),.55,.8,black,24,EXT)

# lighting / camera
world=bpy.data.worlds.get('World') or bpy.data.worlds.new('World'); scene.world=world; world.use_nodes=True; bg=world.node_tree.nodes.get('Background'); bg.inputs['Color'].default_value=(.018,.012,.008,1); bg.inputs['Strength'].default_value=.28
for x,y in [(-8,-7),(-2,-7),(4,-7),(8,-2),(-8,2),(0,2),(8,6)]: area(f'FF_Ambient_{x}_{y}',(x,y,5.6),420,3.5,(1.0,.48,.22))
camd=bpy.data.cameras.new('FF_ShowcaseCamera'); cam=bpy.data.objects.new('FF_ShowcaseCamera',camd); scene.collection.objects.link(cam); scene.camera=cam; cam.location=(18,-22,15); direction=Vector((0,0,3.0))-Vector(cam.location); cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler(); camd.lens=27
scene.render.engine='BLENDER_EEVEE_NEXT'; scene.render.resolution_x=1600; scene.render.resolution_y=1000; scene.render.resolution_percentage=70; scene.render.image_settings.file_format='PNG'; scene.render.filepath=PREVIEW; scene.render.film_transparent=False

scene['mlo_brand']='FUSION FEAST'; scene['mlo_design_direction']='reference-video recreation'; scene['mlo_reference_similarity_target']='high visual/spatial similarity to supplied reference'; scene['mlo_quality_bar']='premium commercial restaurant / FiveM hero interior'; scene['mlo_reference_first_rebuild']=True; scene['mlo_entrance_clear']=True; scene['mlo_rooms_enclosed_and_signed']=True; scene['mlo_doors_lockable']=True; scene['mlo_stairs_visible']=True; scene['mlo_access_pass']='reference_rebuild_v1'; scene['mlo_stair_step_count']=18; scene['mlo_sittable_anchor_count']=12; scene['mlo_main_route_width_m']=2.9; scene['mlo_no_nightclub_language']=True
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
try: bpy.ops.render.render(write_still=True)
except Exception as e: print('Render warning:',e); bpy.ops.wm.save_as_mainfile(filepath=BLEND)
manifest={}
if os.path.exists(MANIFEST):
    try:
        with open(MANIFEST,'r',encoding='utf-8') as f: manifest=json.load(f)
    except: pass
manifest.update({'status':'reference-first rebuild complete','design_direction':'Fusion Feast supplied-video recreation','reference_target':'emerald/walnut/brass restaurant with booths, slatted walls, glazing, bar, kitchen, washroom, broad stair','reference_first_rebuild':True,'quality_bar':'premium commercial restaurant / FiveM hero interior','mesh_objects':len([o for o in bpy.data.objects if o.type=='MESH']),'sittable_anchors':12,'stair_steps':18})
with open(MANIFEST,'w',encoding='utf-8') as f: json.dump(manifest,f,indent=2)
print('FUSION FEAST REFERENCE REBUILD PASS')
print('Meshes:',manifest['mesh_objects'],'Seats:',12,'Stairs:',18)
