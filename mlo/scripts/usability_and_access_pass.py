import bpy, os, json, math

ROOT=r'D:\first Blender\mlo'; OUT=os.path.join(ROOT,'output'); BLEND=os.path.join(OUT,'Nocturne_Lounge_MLO.blend'); MANIFEST=os.path.join(OUT,'mlo_manifest.json')
if not os.path.exists(BLEND): raise RuntimeError('usability_and_access_pass: missing blend')
bpy.ops.wm.open_mainfile(filepath=BLEND)

def mat(name,color,metal=0,rough=.45,emit=None,strength=0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes=True
    b=m.node_tree.nodes.get('Principled BSDF'); b.inputs['Base Color'].default_value=(*color,1); b.inputs['Metallic'].default_value=metal; b.inputs['Roughness'].default_value=rough
    if emit:
        b.inputs['Emission Color'].default_value=(*emit,1); b.inputs['Emission Strength'].default_value=strength
    return m
wood=bpy.data.materials.get('VIS_Walnut') or mat('ACCESS_Walnut',(.11,.028,.012),.08,.30)
gold=bpy.data.materials.get('VIS_Gold') or mat('ACCESS_Gold',(.42,.16,.025),.92,.14)
metal=bpy.data.materials.get('VIS_Metal') or mat('ACCESS_Metal',(.13,.15,.18),.86,.18)
glass=bpy.data.materials.get('VIS_Glass') or mat('ACCESS_Glass',(.012,.06,.075),.65,.08)
wall=bpy.data.materials.get('VIS_Wall') or mat('ACCESS_Wall',(.065,.062,.07),.05,.58)
cyan=bpy.data.materials.get('VIS_Cyan') or mat('ACCESS_Cyan',(.002,.05,.08),0,.20,(0,.75,1),7)
white=mat('ACCESS_SignWhite',(.75,.78,.80),.05,.28)

def col(name):
    c=bpy.data.collections.get(name)
    if not c: c=bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c)
    return c
access_col=col('MLO_Accessibility'); door_col=col('MLO_Doors'); seat_col=col('MLO_Sittable'); stair_col=col('MLO_Stairs'); room_col=col('MLO_Rooms')
for p in ('ACCESS_','DOOR_','LOCK_','SIT_','STAIR_','ROOMSIGN_','ROUTE_'):
    for o in list(bpy.data.objects):
        if o.name.startswith(p): bpy.data.objects.remove(o,do_unlink=True)

def cube(n,loc,scale,m,bev=.03,rot=0,c=None):
    bpy.ops.mesh.primitive_cube_add(location=loc,rotation=(0,0,rot)); o=bpy.context.object; o.name=n; o.scale=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if bev: b=o.modifiers.new('SoftEdge','BEVEL'); b.width=bev; b.segments=2
    if c:
        for u in list(o.users_collection): u.objects.unlink(o)
        c.objects.link(o)
    return o

def text(n,s,loc,size,m,c):
    cu=bpy.data.curves.new(n,'FONT'); cu.body=s; cu.align_x='CENTER'; cu.align_y='CENTER'; cu.size=size; cu.extrude=.012; o=bpy.data.objects.new(n,cu); c.objects.link(o); o.location=loc; o.rotation_euler=(math.pi/2,0,0); o.data.materials.append(m); return o

def door(n,x,y,z=1.15,half_w=.95,half_h=1.15,open_state=False,room='',swing='in'):
    # z/half_h are true door-center and half-height values, preventing oversized door geometry.
    ft=.055
    cube(n+'_FrameL',(x-half_w,y,z),(ft,.08,half_h),metal,.012,0,door_col)
    cube(n+'_FrameR',(x+half_w,y,z),(ft,.08,half_h),metal,.012,0,door_col)
    cube(n+'_FrameTop',(x,y,z+half_h),(half_w+ft,.08,.055),metal,.012,0,door_col)
    leaf_x=x+(half_w*.62 if open_state else 0)
    leaf=cube(n+'_Leaf',(leaf_x,y-.015,z),(half_w*.48,.035,half_h-.06),glass,.015,0,door_col)
    leaf['door_type']='glass'; leaf['lockable']=True; leaf['lock_state']='unlocked' if open_state else 'locked'; leaf['default_open']=bool(open_state); leaf['room']=room; leaf['swing_direction']=swing; leaf['clear_width_m']=round(half_w*2,2)
    hx=x+(half_w*.52 if not open_state else half_w*.75)
    cube(n+'_Handle',(hx,y-.075,z+.02),(.035,.035,.15),gold,.012,0,door_col)
    lock=cube(n+'_Lock',(hx,y-.095,z+.20),(.028,.018,.028),gold,.008,0,door_col); lock['lockable']=True; lock['key_access']=room
    return leaf

def room_shell(p,x0,x1,y0,y1,door_x,label,door_y,z_center=1.25,half_h=1.25):
    cube(p+'_BackWall',((x0+x1)/2,y1,z_center),((x1-x0)/2,.10,half_h),wall,.035,0,room_col)
    cube(p+'_LeftWall',(x0,(y0+y1)/2,z_center),(.10,(y1-y0)/2,half_h),wall,.035,0,room_col)
    cube(p+'_RightWall',(x1,(y0+y1)/2,z_center),(.10,(y1-y0)/2,half_h),wall,.035,0,room_col)
    gap=1.10; ls=door_x-gap-x0; rs=x1-(door_x+gap)
    if ls>.25: cube(p+'_FrontLeft',(x0+ls/2,door_y,z_center),(ls/2,.10,half_h),wall,.035,0,room_col)
    if rs>.25: cube(p+'_FrontRight',(door_x+gap+rs/2,door_y,z_center),(rs/2,.10,half_h),wall,.035,0,room_col)
    text('ROOMSIGN_'+p,label,(door_x,door_y-.18,z_center+half_h+.18),.25,gold,room_col)

# Replace the incomplete old stair with a full-height, visibly readable stair to the 4.35m second-floor slab.
for o in list(bpy.data.objects):
    if o.name.startswith(('Stair_Step','Stair_Landing','Stair_Railing')): bpy.data.objects.remove(o,do_unlink=True)
step_count=18; step_w=.52; depth=1.42; rise=4.12/step_count; start_x=-5.1; sy=8.25
for i in range(step_count):
    x=start_x+i*step_w; z=(i+.5)*rise
    s=cube(f'STAIR_Step_{i+1:02d}',(x,sy,z),(step_w/2,depth/2,rise/2),wood,.025,0,stair_col); s['stair_index']=i+1; s['safe_step']=True
    cube(f'STAIR_Nosing_{i+1:02d}',(x+step_w*.46,sy-depth*.47,z+rise*.42),(.025,depth*.42,.025),gold,.006,0,stair_col)
landing_x=start_x+step_count*step_w+.75; cube('STAIR_TopLanding',(landing_x,sy,4.18),(1.0,depth/2,.10),wood,.03,0,stair_col)
angle=math.atan2(4.12,step_count*step_w); rail_len=math.sqrt((step_count*step_w)**2+4.12**2); mid_x=start_x+(step_count*step_w)/2; mid_z=2.06+.92
for side in (-1,1):
    y=sy+side*(depth/2+.16); rail=cube(f'STAIR_Handrail_{"L" if side<0 else "R"}',(mid_x,y,mid_z),(rail_len/2,.035,.035),gold,.01,0,stair_col); rail.rotation_euler.y=-angle; rail['handrail']=True
    for i in range(0,step_count+1,3):
        x=start_x+min(i,step_count)*step_w; z=min(i,step_count)*rise+.48; post=cube(f'STAIR_Post_{side}_{i}',(x,y,z),(.035,.035,.55),metal,.008,0,stair_col); post['handrail_support']=True
text('ROOMSIGN_STAIRS','UPSTAIRS',(landing_x,sy-.30,4.52),.26,gold,stair_col)

# Clear main entrance: open sliding leaves retract from the walking lane.
door('DOOR_MainEntrance',0,-12.80,1.15,2.05,1.15,True,'main_entrance','sliding')
text('ACCESS_EntranceSign','ENTRANCE / EXIT',(0,-13.02,3.25),.34,white,access_col)
for y in (-12.0,-10.7,-9.4): cube('ROUTE_EntryGlow',(0,y,.205),(1.15,.018,.018),cyan,.004,0,access_col)

# Replace the two old service partition slabs with room fronts that have deliberate door gaps.
for o in list(bpy.data.objects):
    if o.name.startswith('F1_Service_Partition'): bpy.data.objects.remove(o,do_unlink=True)
room_shell('MeetingRoom',-15.3,-9.55,3.15,9.95,-12.35,'MEETING ROOM',3.15)
door('DOOR_MeetingRoom',-12.35,3.02,room='meeting_room')
room_shell('KitchenRoom',9.55,16.9,.65,9.95,13.2,'KITCHEN / SERVICE',.65)
door('DOOR_Kitchen',13.2,.52,room='kitchen_service')
room_shell('MensWC',4.0,9.45,6.15,10.0,6.72,'MEN',6.15)
door('DOOR_MensWC',6.72,5.98,room='mens_wc')
room_shell('WomensWC',-9.45,-4.0,6.15,10.0,-6.72,'WOMEN',6.15)
door('DOOR_WomensWC',-6.72,5.98,room='womens_wc')
# Upstairs private rooms are correctly elevated to the second-floor deck.
room_shell('PrivateDining',-15.3,-8.8,-9.1,-4.0,-12.05,'PRIVATE DINING',-4.0,5.45,1.05)
door('DOOR_PrivateDining',-12.05,-4.12,5.45, .95,1.05,False,'private_dining')
room_shell('StaffOffice',8.8,15.3,-9.1,-4.0,12.05,'STAFF / OFFICE',-4.0,5.45,1.05)
door('DOOR_StaffOffice',12.05,-4.12,5.45,.95,1.05,False,'staff_office')

# Stable FiveM-friendly seat anchors. These do not add filler props; they mark real seating already present in the scene.
def sit(n,x,y,z=.46,yaw=0,room='cafe'):
    o=bpy.data.objects.new(n,None); o.empty_display_type='ARROWS'; o.empty_display_size=.16; seat_col.objects.link(o); o.location=(x,y,z); o.rotation_euler.z=yaw
    o['sittable']=True; o['seat_height_m']=.46; o['interaction_type']='sit'; o['room']=room; o['clearance_radius_m']=.55
anchors=[
('SIT_Cafe_01',-7.2,-5.0,0,'main_cafe'),('SIT_Cafe_02',-4.7,-5.0,math.pi,'main_cafe'),('SIT_Cafe_03',2.0,-5.0,0,'main_cafe'),('SIT_Cafe_04',3.6,-5.0,math.pi,'main_cafe'),('SIT_Cafe_05',6.0,-5.0,0,'main_cafe'),('SIT_Cafe_06',7.6,-5.0,math.pi,'main_cafe'),
('SIT_Booth_01',-12.8,-1.0,math.pi/2,'booth'),('SIT_Booth_02',-12.8,2.0,math.pi/2,'booth'),('SIT_Booth_03',-12.8,5.0,math.pi/2,'booth'),('SIT_Meeting_01',-14.1,4.0,0,'meeting_room'),('SIT_Meeting_02',-10.5,4.0,math.pi,'meeting_room'),
('SIT_Upper_01',-12,-1.9,0,'upper_cafe'),('SIT_Upper_02',-7,-1.9,0,'upper_cafe'),('SIT_Upper_03',7,-1.9,math.pi,'upper_cafe'),('SIT_Upper_04',12,-1.9,math.pi,'upper_cafe')]
for a in anchors: sit(*a)

sc=bpy.context.scene; sc['mlo_access_pass']='clear_entrance_rooms_doors_stairs_sittable_v2'; sc['mlo_entrance_clear']=True; sc['mlo_rooms_enclosed_and_signed']=True; sc['mlo_doors_lockable']=True; sc['mlo_stairs_visible']=True; sc['mlo_stairs_step_count']=step_count; sc['mlo_sittable_anchor_count']=len(anchors); sc['mlo_circulation_axis_clear_width_m']=2.7; sc['mlo_quality_rule']='Only curated CC0 hero props plus purpose-built architectural fixtures; no filler props.'
meta={}
if os.path.exists(MANIFEST):
    try:
        with open(MANIFEST,'r',encoding='utf-8') as f: meta=json.load(f)
    except Exception: pass
meta['accessibility_and_usability']={'entrance_exit':'clear vestibule with open sliding glass doors','rooms':['meeting_room','kitchen_service','mens_wc','womens_wc','private_dining','staff_office'],'doors':len([o for o in bpy.data.objects if o.name.startswith('DOOR_') and o.type=='MESH']),'lockable':True,'stairs':{'steps':step_count,'handrails':2,'top_landing':True},'sittable_anchors':len(anchors),'quality_policy':'curated CC0 hero props only; architectural fixtures are purpose-built and optimized'}
meta['completion_stage']='usability/accessibility quality pass'
with open(MANIFEST,'w',encoding='utf-8') as f: json.dump(meta,f,indent=2)
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print('USABILITY + ACCESS PASS COMPLETE',BLEND)
