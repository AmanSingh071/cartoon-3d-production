import bpy, os, json, math

ROOT = r'D:\first Blender\mlo'
OUT = os.path.join(ROOT, 'output')
BLEND = os.path.join(OUT, 'Nocturne_Lounge_MLO.blend')
PREVIEW = os.path.join(OUT, 'mlo_showcase.png')
MANIFEST = os.path.join(OUT, 'mlo_manifest.json')

# This is a post-build detail/optimization pass. It intentionally reuses the
# existing material library and low-segment primitives instead of adding many
# unique materials or unnecessarily dense meshes.

def getmat(name):
    return bpy.data.materials.get(name)

def cube(name, loc, scale, material, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        m=o.modifiers.new('Detail_Bevel','BEVEL'); m.width=bevel; m.segments=2
    if material: o.data.materials.append(material)
    return o

def cyl(name, loc, radius, depth, material, verts=16):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth, location=loc)
    o=bpy.context.object; o.name=name
    if material: o.data.materials.append(material)
    return o

cyan=getmat('Neon_Cyan'); magenta=getmat('Neon_Magenta'); gold=getmat('Gold')
wood=getmat('Wood_Walnut'); fabric=getmat('Fabric_Charcoal'); trim=getmat('Trim_BrushedMetal')

# ---------- premium wall treatment ----------
# Repeated vertical fins create depth while remaining extremely cheap geometry.
for x in (-5.4,-4.5,-3.6,-2.7,2.7,3.6,4.5,5.4):
    cube('FeatureWall_Fin',(x,9.82,2.15),(0.055,0.08,1.45),gold,0.01)
# Framed panels behind the bar.
for x in (8.2,9.8,11.4):
    cube('Bar_BackPanel',(x,2.12,2.55),(0.55,0.035,1.25),fabric,0.025)
    cube('Bar_PanelTrim',(x,2.07,2.55),(0.59,0.025,1.29),trim,0.012)

# ---------- booth/table detail ----------
for x,y in [(-5.7,5.5),(6.0,-4.0)]:
    for a in range(4):
        ang=a*math.pi/2
        cyl('Booth_Peg',(x+0.72*math.cos(ang),y+0.72*math.sin(ang),0.68),0.035,0.35,gold,12)

# ---------- dance-floor inlay ----------
for x in (-4.0,-2.0,0,2.0,4.0):
    cube('Floor_Inlay',(x,1.9,0.195),(0.025,3.0,0.008),cyan,0.005)
for y in (-0.1,1.9,3.9):
    cube('Floor_Inlay',(0,y,0.198),(4.0,0.025,0.008),magenta,0.005)

# ---------- low-cost ceiling pendants ----------
for x,y in [(-6,-4),(0,-4),(6,-4),(-6,4),(6,4)]:
    cyl('Pendant_Rod',(x,y,3.45),0.025,0.55,trim,12)
    cyl('Pendant_Cap',(x,y,3.12),0.14,0.06,gold,16)

# ---------- optimization metadata ----------
scene=bpy.context.scene
scene['mlo_stage']='detail_pass_01'
scene['optimization_targets']={
    'material_reuse': True,
    'instancing_strategy': 'repeated low-poly architectural modules',
    'target_draw_calls': 'minimize unique materials',
    'collision_strategy': 'simple proxy meshes for gameplay collision',
    'lod_strategy': 'high/medium/low tiers for props',
    'texture_strategy': 'shared atlases/material reuse before unique textures'
}

# Keep render settings appropriate for a preview; actual FiveM assets should be
# exported through the planned Sollumz/CodeWalker pipeline.
scene.render.filepath=PREVIEW
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
bpy.ops.render.render(write_still=True)

manifest={}
if os.path.exists(MANIFEST):
    try:
        with open(MANIFEST,'r',encoding='utf-8') as f: manifest=json.load(f)
    except Exception: manifest={}
manifest.update({
    'status':'detail pass 01 - architecture, lighting and optimization foundation',
    'optimization':'active: reusable low-poly modules, shared materials, collision/LOD strategy',
    'latest_pass':'detail_pass_01'
})
with open(MANIFEST,'w',encoding='utf-8') as f: json.dump(manifest,f,indent=2)
print('MLO ENHANCEMENT COMPLETE:', BLEND)
