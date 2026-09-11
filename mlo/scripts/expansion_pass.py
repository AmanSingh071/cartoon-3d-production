import bpy, math, os, json
from mathutils import Vector

ROOT=r'D:\first Blender\mlo'; BLEND=os.path.join(ROOT,'output','Nocturne_Lounge_MLO.blend')
bpy.ops.wm.open_mainfile(filepath=BLEND)

def M(n,c=(.15,.15,.15,1),metal=0,rough=.45,emit=None,strength=0):
    m=bpy.data.materials.get(n) or bpy.data.materials.new(n); m.use_nodes=True
    b=m.node_tree.nodes.get('Principled BSDF'); b.inputs['Base Color'].default_value=c; b.inputs['Metallic'].default_value=metal; b.inputs['Roughness'].default_value=rough
    if emit: b.inputs['Emission Color'].default_value=(*emit,1); b.inputs['Emission Strength'].default_value=strength
    return m
wood=M('Wood_Walnut'); metal=M('Trim_BrushedMetal'); gold=M('Gold'); leather=M('Leather_DeepBrown'); fabric=M('Fabric_Charcoal'); glass=M('Glass_Tinted'); cyan=M('Neon_Cyan'); mag=M('Neon_Magenta'); amber=M('Neon_Amber'); green=M('Plant_Green'); wall=M('Wall_WarmConcrete')

def cube(n,loc,scale,mat,bev=.03,rot=0):
    bpy.ops.mesh.primitive_cube_add(location=loc,rotation=(0,0,rot)); o=bpy.context.object; o.name=n; o.scale=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(mat)
    if bev: mod=o.modifiers.new('EdgeSoft','BEVEL'); mod.width=bev; mod.segments=2
    return o

def cyl(n,loc,r,d,mat,v=16):
    bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=r,depth=d,location=loc); o=bpy.context.object; o.name=n; o.data.materials.append(mat); return o

def text(n,s,loc,size,mat,rot=(math.pi/2,0,0)):
    cu=bpy.data.curves.new(n,'FONT'); cu.body=s; cu.align_x='CENTER'; cu.size=size; cu.extrude=.01; o=bpy.data.objects.new(n,cu); bpy.context.collection.objects.link(o); o.location=loc; o.rotation_euler=rot; o.data.materials.append(mat); return o

# Collections and semantic metadata
for cn in ['MLO_Architecture','MLO_Floor1','MLO_Floor2','MLO_Service','MLO_Guest','MLO_Exterior','MLO_QualityProps','MLO_GameReady']:
    if not bpy.data.collections.get(cn): bpy.data.collections.new(cn); bpy.context.scene.collection.children.link(bpy.data.collections[cn])

def move(o,cn):
    c=bpy.data.collections[cn]
    for u in list(o.users_collection): u.objects.unlink(o)
    c.objects.link(o)

# Expanded footprint: 36m x 28m. Preserve the original lounge core inside it.
# Ground floor wings, entry vestibule, reception, kitchen, restrooms, meeting room and service corridor.
cube('Expansion_Ground_Slab',(0,-2,0),(18,14,.16),wall,.04)
# north/south side wings and partition walls
for x in (-17.5,17.5): cube('Expansion_Outer_Wall',(x,-2,2.4),(.3,13.6,2.4),wall,.06)
cube('Expansion_Back_Wall',(0,11.7,2.4),(17.5,.3,2.4),wall,.06)
# reception / vestibule near front
cube('Reception_Back',(0,-8.4,1.7),(4.2,.12,1.7),wood,.04); text('Reception_Sign','NOCTURNE CAFE',(0,-8.22,2.65),.42,gold)
for x in (-5.4,5.4): cube('Entrance_Glass_Pier',(x,-12.8,2.0),(.16,.16,2.0),glass,.02)
# floor-1 zoning partitions (architectural shells, open door gaps)
for x in (-9.5,9.5): cube('F1_Service_Partition',(x,3.7,1.55),(.12,7.2,1.55),wall,.03)
# kitchen on east rear: counters, prep islands, hood blocks
cube('Kitchen_Counter',(12.8,5.8,1.0),(3.5,.65,.7),wood,.08)
cube('Kitchen_Prep_Island',(12.0,1.9,1.0),(2.8,.75,.7),metal,.08)
for x in (10.0,12.0,14.0): cube('Kitchen_Station',(x,5.2,1.85),(.75,.55,.85),metal,.05)
cube('Kitchen_Hood',(12.5,7.0,3.25),(3.0,.8,.18),metal,.03)
for x in (10.5,12.5,14.5): cyl('Kitchen_Pendant',(x,3.8,3.35),.10,.05,amber,12)
# meeting room west rear: table, chairs, acoustic wall
cube('Meeting_Table',(-12.2,5.3,1.05),(2.6,1.0,.10),wood,.08)
for x in (-14.1,-12.2,-10.3):
    for y in (4.0,6.6): cube('Meeting_Chair',(x,y,.65),(.34,.34,.45),leather,.12)
cube('Meeting_Display_Wall',(-12.2,8.5,1.8),(2.8,.08,1.25),fabric,.02)
text('Meeting_Sign','MEETING',(-12.2,8.35,2.5),.32,cyan)
# bathrooms: two compact rooms with stalls, sinks and mirrors
for side in (-1,1):
    x=side*7.0; cube('Bathroom_Back',(x,8.5,1.5),(3.0,.12,1.5),wall,.03)
    for yy in (7.1,8.4,9.7): cube('Bathroom_Stall',(x+side*1.5,yy,1.1),(.75,.5,1.1),wood,.04)
    for yy in (7.0,8.3,9.6): cyl('Bathroom_Sink',(x-side*1.25,yy,.95),.28,.16,glass,16)
    cube('Bathroom_Mirror',(x-side*1.5,8.4,1.85),(.03,1.8,.75),glass,.01)
    text('Bathroom_Sign','WC', (x,8.05,2.55),.32,gold)
# staircase + landing
for i in range(12): cube('Stair_Step',(-2.5+i*.42,8.8,.18+i*.25),(.18,1.5,.12),wood,.025)
cube('Stair_Landing',(3.0,8.8,3.25),(2.2,1.5,.16),wood,.03)
for x in (-2.5,3.0): cube('Stair_Railing',(x,7.45,2.2),(.04,.04,1.8),gold,.01)
# first-floor slab and balcony around central void
cube('Second_Floor_Slab',(0,1.0,4.35),(17.2,9.6,.18),wall,.04)
# central void opens above the original lounge; balcony rails on three sides
for y in (-7.5,0.0,8.5):
    span=10.5 if y==-7.5 else 15.0
    cube('Balcony_Rail_Top',(0,y,5.25),(span,.06,.06),gold,.01)
    for x in range(-int(span)+1,int(span),2): cube('Balcony_Rail_Vert',(x,y,4.8),(.035,.035,.48),metal,.008)
# upper-floor cafe seating: booths, tables, window lounge
for x,y in [(-12,-1),(-7,-1),(7,-1),(12,-1),(-11,5),(11,5)]:
    cube('Upper_Bench',(x,y,5.05),(1.5,.55,.42),leather,.16)
    cyl('Upper_Table',(x,y-.9,5.05),.65,.10,gold,20)
    for dx in (-.75,.75): cube('Upper_Chair',(x+dx,y-.9,4.75),(.3,.3,.42),fabric,.1)
# upper private dining / quiet room in southwest
cube('Private_Dining_Back',(-12,-7.0,5.8),(3.4,.10,1.2),wood,.04)
for x in (-14,-12,-10): cyl('Private_Dining_Lamp',(x,-6.5,7.0),.08,.04,amber,12)
cube('Private_Dining_Table',(-12,-4.9,5.1),(2.2,.85,.10),wood,.06)
# upper office / staff room in southeast
cube('Staff_Office_Back',(12,-7.0,5.8),(3.4,.10,1.2),wall,.04)
cube('Staff_Desk',(12,-5.2,5.15),(2.0,.7,.10),wood,.05)
text('Staff_Sign','STAFF / OFFICE',(12,-6.8,6.5),.30,cyan)
# upper feature bar / coffee counter
cube('Coffee_Counter',(0,7.0,5.2),(4.0,.7,.75),wood,.10); cube('Coffee_Top',(0,7.0,6.03),(4.1,.78,.08),gold,.03)
for x in (-2.8,-1.4,0,1.4,2.8): cyl('Coffee_Pendant',(x,6.1,7.2),.10,.05,amber,12)
# aesthetic greenery: stylized clustered foliage instead of sparse low-quality leaves
for x,y in [(-15,-10),(15,-10),(-15,10),(15,10),(-4,4),(4,4)]:
    cyl('Quality_Planter',(x,y,.55),.55,.85,wood,20)
    for a in range(0,360,45):
        z=1.5+(a%90)*.004; leaf=cyl('Quality_Leaf',(x+.45*math.cos(math.radians(a)),y+.45*math.sin(math.radians(a)),z),.12,.9,green,10); leaf.rotation_euler=(.45*math.sin(math.radians(a)),.45*math.cos(math.radians(a)),math.radians(a))
# lighting: restrained architectural fixtures, not hundreds of lights
for x in (-14,-7,0,7,14):
    for y in (-10,-3,4,10):
        cyl('F2_Ceiling_Downlight',(x,y,7.75),.09,.05,amber,12)
# upper floor perimeter glazing accents
for x in (-16,-12,-8,8,12,16):
    cube('Upper_Window_Frame',(x,-10.5,5.8),(1.3,.05,1.35),metal,.02)
    cube('Upper_Window_Glass',(x,-10.43,5.8),(1.12,.02,1.15),glass,.01)
# exterior canopy and signage
cube('Entrance_Canopy',(0,-13.3,4.0),(6.2,1.3,.18),wood,.06); cube('Entrance_Canopy_Glow',(0,-12.0,3.85),(5.7,.035,.06),cyan,.01)
text('Exterior_Title','NOCTURNE',(0,-13.0,3.65),.65,gold)
# metadata
sc=bpy.context.scene; sc['mlo_expansion']='two_story_cafe_v2'; sc['floor_count']=2; sc['footprint_m']=[36,28]
sc['rooms_extended']='Entrance, Reception, Main Cafe, Lounge, Bar, DJ, VIP, Meeting, Kitchen, Male WC, Female WC, Stair, Upper Cafe, Private Dining, Staff Office, Coffee Bar'
sc['quality_props']='upgraded planters, architectural glazing, premium signage, layered cafe furniture'
sc['optimization']='shared materials; low-poly primitives; semantic collections; restrained lights; no texture image dependency'
# move obvious expansion objects into semantic collections
prefixes={'F2_':'MLO_Floor2','Upper_':'MLO_Floor2','Private_':'MLO_Floor2','Staff_':'MLO_Floor2','Coffee_':'MLO_Floor2','Balcony_':'MLO_Floor2','Expansion_':'MLO_Architecture','Kitchen_':'MLO_Service','Meeting_':'MLO_Service','Bathroom_':'MLO_Service','Stair_':'MLO_Architecture','Quality_':'MLO_QualityProps','Entrance_':'MLO_Exterior','Exterior_':'MLO_Exterior'}
for o in list(sc.objects):
    for p,c in prefixes.items():
        if o.name.startswith(p): move(o,c); break
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print('EXPANSION PASS COMPLETE',BLEND)
