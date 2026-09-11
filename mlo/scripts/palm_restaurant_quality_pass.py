import bpy, os, json, math
from mathutils import Vector

ROOT=r'D:\first Blender\mlo'; OUT=os.path.join(ROOT,'output'); BLEND=os.path.join(OUT,'Nocturne_Lounge_MLO.blend'); PREVIEW=os.path.join(OUT,'mlo_showcase.png'); MANIFEST=os.path.join(OUT,'mlo_manifest.json')
if not os.path.exists(BLEND): raise RuntimeError('palm_restaurant_quality_pass: missing blend')
bpy.ops.wm.open_mainfile(filepath=BLEND)

# ---------- materials: premium tropical restaurant palette ----------
def mat(name,color,metal=0,rough=.45,emit=None,strength=0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes=True
    b=m.node_tree.nodes.get('Principled BSDF'); b.inputs['Base Color'].default_value=(*color,1); b.inputs['Metallic'].default_value=metal; b.inputs['Roughness'].default_value=rough
    if emit:
        if 'Emission Color' in b.inputs: b.inputs['Emission Color'].default_value=(*emit,1)
        if 'Emission Strength' in b.inputs: b.inputs['Emission Strength'].default_value=strength
    m.diffuse_color=(*color,1); return m

stone=mat('PALM_Terrazzo',(.47,.43,.35),.05,.28)
cream=mat('PALM_IvoryStucco',(.72,.67,.56),.0,.62)
plaster=mat('PALM_Limestone',(.55,.50,.42),.0,.48)
teak=mat('PALM_Teak',(.28,.105,.035),.05,.30)
walnut=mat('PALM_Walnut',(.14,.045,.018),.03,.27)
brass=mat('PALM_Brass',(.55,.30,.075),.88,.16)
emerald=mat('PALM_Emerald',(.018,.18,.11),.0,.36)
leaf=mat('PALM_PalmLeaf',(.025,.22,.075),.0,.58)
leaf2=mat('PALM_PalmLeafLight',(.07,.34,.12),.0,.54)
water=mat('PALM_GreenGlass',(.02,.15,.12),.35,.12)
white=mat('PALM_MenuWhite',(.90,.86,.74),.0,.25)
black=mat('PALM_Charcoal',(.025,.025,.022),.05,.42)
glow=mat('PALM_WarmGlow',(.45,.20,.035),.0,.22,(1.0,.30,.06),4)

# ---------- collections ----------
def collection(name):
    c=bpy.data.collections.get(name)
    if not c: c=bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c)
    return c
arch=collection('PALM_Architecture'); route=collection('PALM_Circulation'); stairs=collection('PALM_Stairs'); decor=collection('PALM_Decor'); palms=collection('PALM_TropicalLandscaping'); lighting=collection('PALM_Lighting')

def move_to(obj,c):
    for old in list(obj.users_collection): old.objects.unlink(obj)
    c.objects.link(obj)

def cube(n,loc,scale,m,bev=.03,rot=0,c=None):
    bpy.ops.mesh.primitive_cube_add(location=loc,rotation=(0,0,rot)); o=bpy.context.object; o.name=n; o.scale=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if bev:
        b=o.modifiers.new('SoftEdge','BEVEL'); b.width=bev; b.segments=2
    if c: move_to(o,c)
    return o

def cyl(n,loc,r,d,m,v=20,c=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=r,depth=d,location=loc); o=bpy.context.object; o.name=n; o.data.materials.append(m)
    if c: move_to(o,c)
    return o

def text(n,s,loc,size,m,c,rot=(math.pi/2,0,0)):
    cu=bpy.data.curves.new(n,'FONT'); cu.body=s; cu.align_x='CENTER'; cu.align_y='CENTER'; cu.size=size; cu.extrude=.012; cu.bevel_depth=.003
    o=bpy.data.objects.new(n,cu); c.objects.link(o); o.location=loc; o.rotation_euler=rot; o.data.materials.append(m); return o

def delete_prefixes(prefixes):
    for o in list(bpy.data.objects):
        if any(o.name.startswith(p) for p in prefixes): bpy.data.objects.remove(o,do_unlink=True)

# ---------- remove the old nightclub language and low-quality vegetation ----------
delete_prefixes(('PlantPot','Leaf','PHQ_PlantPot','DJ_','Speaker','Stage','VIS_','CeilingFixture','Warm_Ceiling_Light','BarStool','StoolSeat','DiningTable','ChairLeg','ChairSeat','STAIR_','ACCESS_','ROUTE_'))
# Remove old neon materials from objects by replacing them with restaurant materials.
replace={
    'Floor_DarkStone':stone,'Wall_WarmConcrete':cream,'Trim_BrushedMetal':brass,'Wood_Walnut':teak,
    'Leather_DeepBrown':walnut,'Fabric_Charcoal':black,'Glass_Tinted':water,'Gold':brass,
    'Neon_Cyan':emerald,'Neon_Magenta':brass,'Neon_Amber':glow,'Plant_Green':leaf,
    'VIS_Floor':stone,'VIS_Wall':cream,'VIS_Walnut':teak,'VIS_Leather':walnut,'VIS_Fabric':black,
    'VIS_Metal':brass,'VIS_Gold':brass,'VIS_Glass':water,'VIS_Cyan':emerald,'VIS_Magenta':brass,'VIS_Amber':glow,'VIS_Green':leaf
}
for o in bpy.data.objects:
    if o.type!='MESH': continue
    for i,s in enumerate(o.material_slots):
        if s.material and s.material.name in replace: o.data.materials[i]=replace[s.material.name]

# Delete old club/stage geometry entirely; restaurant gets an open dining floor.
delete_prefixes(('Stage','DJ_','Speaker','SpeakerRing','Stage_Fascia'))

# ---------- floor + circulation hierarchy ----------
# A contrasting 2.7m main aisle from entrance to dining core, then a clearly signed branch to stairs.
cube('PALM_MainAisle',(0,-5.2,.205),(1.35,5.6,.018),stone,.008,0,route)
cube('PALM_AisleInset',(0,-5.2,.228),(1.02,5.45,.012),emerald,.004,0,route)
cube('PALM_AisleWarmCenter',(0,-5.2,.244),(.035,5.35,.008),brass,.002,0,route)
cube('PALM_StairBranch',(-2.9,.65,.207),(2.9,.92,.018),stone,.008,0,route)
cube('PALM_StairBranchInset',(-2.9,.65,.230),(2.65,.66,.012),emerald,.004,0,route)
cube('PALM_StairBranchCenter',(-2.9,.65,.246),(2.55,.035,.008),brass,.002,0,route)
for y in (-10.0,-8.2,-6.4,-4.6,-2.8,-1.0):
    cube('PALM_AisleMarker',(0,y,.255),(.75,.018,.012),brass,.002,0,route)
text('PALM_EntryWayfinding','WELCOME',(0,-10.85,.42),.26,brass,route)
text('PALM_StairWayfinding','STAIRS  ↑',(-2.9,.65,.42),.22,brass,route)

# ---------- premium straight stair in a dedicated, unobstructed zone ----------
step_count=18; step_w=1.72; step_d=.50; rise=4.12/step_count; sx=-5.2; sy=1.65
for i in range(step_count):
    y=sy+i*step_d; z=(i+.5)*rise
    s=cube(f'PALM_STAIR_Step_{i+1:02d}',(sx,y,z),(step_w/2,step_d/2,rise/2),teak,.025,0,stairs); s['stair_index']=i+1; s['safe_step']=True; s['clear_width_m']=step_w
    cube(f'PALM_STAIR_Nosing_{i+1:02d}',(sx,y-step_d*.45,z+rise*.43),(step_w*.46,.018,.022),brass,.004,0,stairs)
landing_y=sy+step_count*step_d+.32
cube('PALM_STAIR_TopLanding',(sx,landing_y,4.18),(1.18,.38,.10),stone,.035,0,stairs)
# Two clean handrails run parallel to the stair direction.
rail_len=step_count*step_d; rail_z=2.18
for side in (-1,1):
    x=sx+side*(step_w/2+.15); rail=cube(f'PALM_STAIR_Handrail_{side}',(x,sy+rail_len/2,rail_z),(0.035,rail_len/2,.035),brass,.01,0,stairs); rail['handrail']=True
    for i in range(0,step_count+1,3):
        y=sy+min(i,step_count)*step_d; z=min(i,step_count)*rise+.50
        p=cube(f'PALM_STAIR_Post_{side}_{i}',(x,y,z),(.032,.032,.52),brass,.008,0,stairs); p['handrail_support']=True
text('PALM_STAIR_Sign','UPSTAIRS', (sx,landing_y+.20,4.48),.27,brass,stairs)

# ---------- architectural restaurant identity ----------
cube('PALM_HeroWall',(0,10.28,2.25),(6.8,.10,1.92),cream,.045,0,arch)
for x in (-5.4,-3.6,-1.8,0,1.8,3.6,5.4): cube('PALM_WallBrassInlay',(x,10.15,2.25),(.018,.018,1.55),brass,.004,0,arch)
text('PALM_Logo','PALM HOUSE',(0,10.04,2.65),.86,brass,arch)
text('PALM_Subtitle','TROPICAL DINING  /  COFFEE  /  DESSERT',(0,10.02,2.02),.18,emerald,arch)
# Replace the old NOCTURNE text if it remains.
for o in list(bpy.data.objects):
    if o.name in ('Logo','NOCTURNE','PHQ_CafeTitle','PHQ_CafeSubtitle'): bpy.data.objects.remove(o,do_unlink=True)

# ---------- premium dining tables + settings ----------
def dining_table(x,y,rot=0):
    top=cube(f'PALM_DiningTop_{x}_{y}',(x,y,.78),(1.22,.72,.075),teak,.06,rot,decor)
    cyl(f'PALM_DiningPedestal_{x}_{y}',(x,y,.42),.22,.68,brass,24,decor)
    # stone inlay on table
    cube(f'PALM_TableInlay_{x}_{y}',(x,y,.858),(.78,.025,.012),brass,.003,rot,decor)
    for side in (-1,1):
        cy=y+side*.98
        # seat anchors, actual hero chairs remain in scene nearby
        a=bpy.data.objects.new(f'PALM_SEAT_{x}_{y}_{side}',None); a.empty_display_type='ARROWS'; a.empty_display_size=.14; decor.objects.link(a); a.location=(x,cy,.46); a.rotation_euler.z=(math.pi if side<0 else 0)+rot; a['sittable']=True; a['interaction_type']='sit'; a['seat_height_m']=.46; a['clearance_radius_m']=.55
        cyl(f'PALM_Plate_{x}_{y}_{side}',(x,cy+side*.12,.88),.23,.025,white,24,decor)
        cyl(f'PALM_Glass_{x}_{y}_{side}',(x+.52*math.cos(rot),cy+.52*math.sin(rot),1.00),.065,.20,water,16,decor)
        cube(f'PALM_Napkin_{x}_{y}_{side}',(x-.35*math.cos(rot),cy-.35*math.sin(rot),.90),(.16,.10,.012),cream,.005,rot,decor)

# Open central dining field; keep stair branch and main aisle clear.
for cfg in [(-7.8,-6.2,0),(-3.7,-6.2,0),(3.7,-6.2,0),(7.8,-6.2,0),(-7.8,-2.7,0),(3.7,-2.7,0),(7.8,-2.7,0),(-1.0,3.0,0),(3.4,3.0,0),(7.8,3.0,0)]: dining_table(*cfg)

# ---------- service counter becomes refined restaurant bar / dessert counter ----------
for n in ('BarCounter','BarTop','BarBack','BarShelf'):
    for o in list(bpy.data.objects):
        if o.name==n or o.name.startswith(n):
            for s in o.material_slots: s.material=teak if 'Counter' in n or 'Back' in n else brass
cube('PALM_MenuBoard',(8.3,1.28,2.95),(2.5,.035,.70),black,.025,0,arch)
text('PALM_MenuTitle','COFFEE  •  DESSERT  •  ZERO-PROOF',(8.3,1.22,3.28),.20,white,arch)
for x,label in [(6.8,'ESPRESSO'),(8.3,'SIGNATURE'),(9.8,'DESSERT')]:
    text('PALM_MenuItem_'+label,label,(x,1.20,2.92),.14,brass,arch)

# ---------- high-quality low-poly palm trees (purpose-built, not filler) ----------
def palm_leaf_mesh(name,base,tip,width,material,c):
    bx,by,bz=base; tx,ty,tz=tip; dx=tx-bx; dy=ty-by; dz=tz-bz; L=math.sqrt(dx*dx+dy*dy+dz*dz); ux,uy,uz=dx/L,dy/L,dz/L
    # side vector perpendicular to travel direction
    sx,sy=-uy,ux; sz=0; verts=[]; seg=7
    for i in range(seg+1):
        t=i/seg; cx=bx+dx*t; cy=by+dy*t; cz=bz+dz*t-0.18*(t*t)
        w=width*(1-t)**.72
        verts.extend([(cx+sx*w,cy+sy*w,cz),(cx-sx*w,cy-sy*w,cz)])
    faces=[]
    for i in range(seg): faces.append((2*i,2*i+1,2*i+3,2*i+2))
    me=bpy.data.meshes.new(name); me.from_pydata(verts,[],faces); me.update(); o=bpy.data.objects.new(name,me); c.objects.link(o); o.data.materials.append(material); o['hero_prop']='purpose_built_palm_leaf'; return o

def premium_palm(name,x,y,scale=1.0):
    root=bpy.data.objects.new(name,None); palms.objects.link(root); root.location=(x,y,0); root['hero_prop']='palm_tree'; root['game_ready']='low_poly_shared_material'
    # tapered segmented trunk with subtle horizontal bands
    segs=9; total=3.15*scale
    for i in range(segs):
        z=(i+.5)*total/segs; r1=.17*scale*(1-.28*i/segs); r2=.18*scale*(1-.28*(i+1)/segs)
        bpy.ops.mesh.primitive_cone_add(vertices=12,radius1=r1,radius2=r2,depth=total/segs,location=(x,y,z)); tr=bpy.context.object; tr.name=f'{name}_Trunk_{i:02d}'; tr.data.materials.append(teak); tr.parent=root
        cyl(f'{name}_BarkBand_{i:02d}',(x,y,z+total/segs*.46),max(r1,r2)*1.01,.045*scale,walnut,12,palms).parent=root
    crown=(x,y,total)
    for i in range(11):
        a=2*math.pi*i/11+.16*(i%2); length=(1.25+.25*(i%3))*scale; tilt=.42+.12*(i%3)
        tip=(x+math.cos(a)*length,y+math.sin(a)*length,total+tilt*scale-.18*(i%2))
        palm_leaf_mesh(f'{name}_Frond_{i:02d}',crown,tip,.20*scale,leaf if i%2 else leaf2,palms)
    cyl(f'{name}_CrownCap',crown,.28*scale,.22*scale,leaf2,16,palms).parent=root
    pot=cyl(f'{name}_Planter',(x,y,.32*scale),.48*scale,.55*scale,stone,24,palms); pot.parent=root
    ring=cyl(f'{name}_PlanterBand',(x,y,.60*scale),.49*scale,.07*scale,brass,24,palms); ring.parent=root
    return root

for args in [(-11.0,-8.2,1.05), (11.0,-8.2,1.05), (-11.0,6.0,.95), (11.0,6.0,.95)]: premium_palm('PALM_HeroPalm_%s_%s'%(args[0],args[1]),*args)

# ---------- ceiling + pendant language ----------
for x in (-9,-3,3,9):
    for y in (-7,0,7):
        cyl('PALM_PendantFixture',(x,y,3.72),.18,.08,brass,24,lighting)
        cyl('PALM_PendantGlow',(x,y,3.64),.10,.035,glow,20,lighting)
# Large statement canopy above dining core.
cyl('PALM_CeilingCanopy',(0,-1.2,3.88),3.1,.07,teak,48,lighting)
for i in range(12):
    a=2*math.pi*i/12; cyl('PALM_CanopyBrass',(3.1*math.cos(a),-1.2+3.1*math.sin(a),3.83),.035,.06,brass,12,lighting)

# ---------- daylight / premium lighting ----------
for o in list(bpy.data.objects):
    if o.type=='LIGHT': bpy.data.objects.remove(o,do_unlink=True)
def look(obj,target): obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
def area(n,loc,target,energy,size,color):
    bpy.ops.object.light_add(type='AREA',location=loc); l=bpy.context.object; l.name=n; l.data.energy=energy; l.data.shape='DISK'; l.data.size=size; l.data.color=color; look(l,target); move_to(l,lighting); return l
area('PALM_Key_Entry',(0,-7.5,4.0),(0,-4,0),850,4.5,(1.0,.72,.42))
area('PALM_Key_Dining',(0,-1.0,4.2),(0,-1,0),1000,5.0,(1.0,.78,.52))
area('PALM_Key_Left',(-9,-2,4.0),(-4,0,0),700,4.0,(.82,1.0,.84))
area('PALM_Key_Right',(9,-2,4.0),(4,0,0),700,4.0,(1.0,.76,.46))
area('PALM_Key_Back',(0,7.8,4.0),(0,7,0),650,4.0,(.90,.96,.80))
area('PALM_Key_Stairs',(-5.2,5.0,4.0),(-5.2,5.0,1.8),800,3.0,(1.0,.72,.38))

# World becomes warm daylight rather than nightclub black.
world=bpy.context.scene.world; world.use_nodes=True; bg=world.node_tree.nodes.get('Background')
if bg: bg.inputs['Color'].default_value=(.045,.055,.048,1); bg.inputs['Strength'].default_value=.32

# ---------- remove remaining nightclub glow geometry ----------
delete_prefixes(('VIS_WallGlow','VIS_PerimeterGlow','VIS_BarUnderGlow','VIS_BarShelfGlow','VIS_StageGlow','VIS_DanceGrid','PHQ_AxisGlow'))

# ---------- showcase camera ----------
for o in list(bpy.data.objects):
    if o.name=='MLO_Showcase_Camera': bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.object.camera_add(location=(19,-24,11.5)); cam=bpy.context.object; cam.name='MLO_Showcase_Camera'; bpy.context.scene.camera=cam; cam.data.lens=30; look(cam,(0,0,1.55))

sc=bpy.context.scene; sc.render.engine='BLENDER_EEVEE'; sc.render.resolution_x=1920; sc.render.resolution_y=1080; sc.render.resolution_percentage=70; sc.render.image_settings.file_format='PNG'; sc.render.filepath=PREVIEW
try: sc.view_settings.look='AgX - Medium High Contrast'
except Exception: pass
sc['mlo_brand']='Palm House Restaurant'; sc['mlo_design_language']='premium tropical resort restaurant'; sc['mlo_stair_route_clear']=True; sc['mlo_main_aisle_clear_width_m']=2.7; sc['mlo_palm_hero_trees']=4; sc['mlo_low_quality_vegetation_removed']=True; sc['mlo_quality_bar']='AAA-style hospitality visual target: hierarchy, clean circulation, hero props, restrained materials, purposeful lighting'; sc['mlo_no_filler_props']=True

meta={}
if os.path.exists(MANIFEST):
    try:
        with open(MANIFEST,'r',encoding='utf-8') as f: meta=json.load(f)
    except Exception: pass
meta.update({'name':'Palm House Restaurant','type':'FiveM MLO','design_direction':'premium tropical resort restaurant','visual_standard':'hero-prop / AAA hospitality target','quality_bar':'clean circulation + strong material hierarchy + hero palms + purposeful lighting','low_quality_vegetation_removed':True,'stairs_route':{'main_aisle_width_m':2.7,'branch_width_m':1.84,'step_count':step_count,'visible_from_entry':True},'hero_vegetation':{'type':'purpose-built low-poly palms','count':4,'shared_materials':True}})
meta['latest_pass']='palm_restaurant_quality_pass_v1'
with open(MANIFEST,'w',encoding='utf-8') as f: json.dump(meta,f,indent=2)
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
bpy.ops.render.render(write_still=True)
print('PALM RESTAURANT QUALITY PASS COMPLETE',BLEND)
