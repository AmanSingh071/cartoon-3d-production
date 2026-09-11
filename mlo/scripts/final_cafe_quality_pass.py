import bpy, os, json, math, urllib.request, hashlib
from mathutils import Vector

ROOT = r'D:\first Blender\mlo'
OUT = os.path.join(ROOT, 'output')
BLEND = os.path.join(OUT, 'Nocturne_Lounge_MLO.blend')
CACHE = os.path.join(ROOT, 'asset_cache')
MANIFEST = os.path.join(OUT, 'mlo_manifest.json')
os.makedirs(CACHE, exist_ok=True)

if not os.path.exists(BLEND):
    raise RuntimeError('final_cafe_quality_pass: missing blend')

bpy.ops.wm.open_mainfile(filepath=BLEND)

# Curated CC0 hero props from Poly Haven. The build downloads 2K Blender variants
# at runtime so the Git repository stays source-only and the final scene stays sane.
ASSETS = {
    'modern_arm_chair_01': {'positions': [(-7.2,-5.0,0.0, 0.0), (-4.7,-5.0,0.0, math.pi)], 'scale': 1.0},
    'sofa_01': {'positions': [(-7.0,-2.2,0.0, 0.0)], 'scale': 1.0},
    'modern_coffee_table_01': {'positions': [(-7.0,-3.9,0.0, 0.0)], 'scale': 1.0},
    'round_wooden_table_01': {'positions': [(2.8,-5.0,0.0, 0.0), (6.8,-5.0,0.0, 0.0)], 'scale': 0.85},
    'painted_wooden_chair_01': {'positions': [(2.0,-5.0,0.0, 0.0),(3.6,-5.0,0.0, math.pi),(6.0,-5.0,0.0, 0.0),(7.6,-5.0,0.0, math.pi)], 'scale': 0.9},
}

API = 'https://api.polyhaven.com'
UA = 'NocturneCafeBuilder/1.0'

def get_json(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.loads(r.read().decode('utf-8'))

def choose_file(tree, wanted_res=('2k','4k','1k','8k')):
    block = tree.get('blend') or {}
    for res in wanted_res:
        if res in block and isinstance(block[res], dict):
            node = block[res].get('blend')
            if isinstance(node, dict) and node.get('url'):
                return res, node['url']
    for res, data in block.items():
        if isinstance(data, dict):
            node = data.get('blend')
            if isinstance(node, dict) and node.get('url'):
                return res, node['url']
    return None, None

def download_asset(asset_id):
    target = os.path.join(CACHE, asset_id + '.blend')
    if os.path.exists(target) and os.path.getsize(target) > 10000:
        return target, 'cached'
    files = get_json(f'{API}/files/{asset_id}')
    res, url = choose_file(files)
    if not url:
        raise RuntimeError(f'No Blender file found for {asset_id}')
    print(f'DOWNLOAD {asset_id} [{res}]')
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=180) as r, open(target, 'wb') as f:
        while True:
            chunk = r.read(1024*1024)
            if not chunk: break
            f.write(chunk)
    if os.path.getsize(target) <= 10000:
        raise RuntimeError(f'Bad asset download: {asset_id}')
    return target, res

def append_collection(filepath, asset_id):
    before = set(bpy.data.objects.keys())
    with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
        names = list(data_from.collections)
        chosen = asset_id if asset_id in names else (names[0] if names else None)
        if not chosen:
            raise RuntimeError(f'No collection in {asset_id}.blend')
        data_to.collections = [chosen]
    col = data_to.collections[0]
    bpy.context.scene.collection.children.link(col)
    new_objs = [o for o in col.all_objects if o.name not in before]
    return col, new_objs

def make_root(name, objs, loc, scale, rot):
    root = bpy.data.objects.new(name, None)
    root.empty_display_type = 'PLAIN_AXES'
    bpy.context.scene.collection.objects.link(root)
    for o in objs:
        if o.parent is None:
            o.parent = root
    root.location = loc
    root.rotation_euler.z = rot
    root.scale = (scale, scale, scale)
    root['fivem_asset']='polyhaven_cc0'
    root['asset_resolution']='2k_or_best'
    return root

# Remove only a previous run of this pass; never touch authored architecture.
for o in list(bpy.data.objects):
    if o.name.startswith('PHQ_'):
        bpy.data.objects.remove(o, do_unlink=True)
for c in list(bpy.data.collections):
    if c.name.startswith('PHQ_'):
        bpy.data.collections.remove(c)

asset_stats=[]
for asset_id, cfg in ASSETS.items():
    path, res = download_asset(asset_id)
    base_col, objs = append_collection(path, asset_id)
    # Imported asset collection becomes a child of a dedicated semantic collection.
    parent_col = bpy.data.collections.get('MLO_QualityProps')
    if not parent_col:
        parent_col=bpy.data.collections.new('MLO_QualityProps'); bpy.context.scene.collection.children.link(parent_col)
    for obj in list(objs):
        for c in list(obj.users_collection): c.objects.unlink(obj)
        parent_col.objects.link(obj)
    for idx,(x,y,z,rot) in enumerate(cfg['positions']):
        copies=[]
        if idx == 0:
            copies=objs
        else:
            for obj in objs:
                cp=obj.copy()
                if obj.data: cp.data=obj.data.copy()
                parent_col.objects.link(cp); copies.append(cp)
        root=make_root(f'PHQ_{asset_id}_{idx:02d}', copies, (x,y,z), cfg['scale'], rot)
    # Keep the source collection hidden after its objects have been transferred.
    try: bpy.data.collections.remove(base_col)
    except Exception: pass
    asset_stats.append({'id':asset_id,'resolution':res,'instances':len(cfg['positions'])})

# Premium first-floor architecture: a proper cafe spine rather than a sparse blockout.
def mat(name, color, metal=0.0, rough=.45, emission=None, strength=0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Metallic'].default_value=metal; bs.inputs['Roughness'].default_value=rough
    if emission:
        if 'Emission Color' in bs.inputs: bs.inputs['Emission Color'].default_value=(*emission,1)
        if 'Emission Strength' in bs.inputs: bs.inputs['Emission Strength'].default_value=strength
    return m

def cube(n,loc,scale,m,bev=.03,rot=0):
    bpy.ops.mesh.primitive_cube_add(location=loc,rotation=(0,0,rot)); o=bpy.context.object; o.name=n; o.scale=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if bev:
        b=o.modifiers.new('PremiumEdge','BEVEL'); b.width=bev; b.segments=2
    return o

def cyl(n,loc,r,d,m,v=20):
    bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=r,depth=d,location=loc); o=bpy.context.object; o.name=n; o.data.materials.append(m); return o

def text(n,s,loc,size,m):
    cu=bpy.data.curves.new(n,'FONT'); cu.body=s; cu.align_x='CENTER'; cu.size=size; cu.extrude=.012; o=bpy.data.objects.new(n,cu); bpy.context.scene.collection.objects.link(o); o.location=loc; o.rotation_euler=(math.pi/2,0,0); o.data.materials.append(m); return o

wood=bpy.data.materials.get('VIS_Walnut') or mat('VIS_Walnut',(.12,.035,.015),.08,.28)
gold=bpy.data.materials.get('VIS_Gold') or mat('VIS_Gold',(.42,.16,.025),.92,.14)
cyan=bpy.data.materials.get('VIS_Cyan') or mat('VIS_Cyan',(.002,.05,.08),0,.2,(0,.75,1),7)
mag=bpy.data.materials.get('VIS_Magenta') or mat('VIS_Magenta',(.06,.002,.035),0,.2,(1,.01,.35),7)
wall=bpy.data.materials.get('VIS_Wall') or mat('VIS_Wall',(.07,.065,.075),.05,.58)
metal=bpy.data.materials.get('VIS_Metal') or mat('VIS_Metal',(.16,.18,.21),.82,.2)
leather=bpy.data.materials.get('VIS_Leather') or mat('VIS_Leather',(.055,.012,.018),0,.32)

# Front-of-house cafe identity wall and menu spine.
cube('PHQ_CafeFeatureWall',(0,-10.0,2.25),(7.2,.10,2.25),wall,.04)
for x in (-5.8,-3.8,-1.8,0,1.8,3.8,5.8): cube('PHQ_WallInlay',(x,-9.84,2.25),(.025,.025,1.75),gold,.006)
text('PHQ_CafeTitle','NOCTURNE',(0,-9.72,3.1),.72,gold)
text('PHQ_CafeSubtitle','COFFEE  /  PASTRY  /  LOUNGE',(0,-9.70,2.15),.23,cyan)

# Service counter upgrade: layered face, pastry display, menu header and shelving.
cube('PHQ_CounterFace',(8.8,-2.0,1.05),(3.8,.62,.85),wood,.10)
cube('PHQ_CounterStone',(8.8,-2.0,1.93),(4.0,.70,.10),gold,.035)
cube('PHQ_PastryDisplay',(8.8,-1.28,1.45),(2.25,.28,.72),metal,.06)
for z in (1.15,1.48,1.81): cube('PHQ_DisplayShelf',(8.8,-.96,z),(2.0,.05,.025),glass,.006)
for x in (7.1,8.3,9.5,10.7): cyl('PHQ_DisplayPlate',(x,-1.15,1.20),.28,.035,glass,20)
for x in (7.2,8.8,10.4): cube('PHQ_MenuPanel',(x,.0,2.65),(1.05,.035,.72),wall,.025)
text('PHQ_MenuHeader','COFFEE  |  TEA  |  PASTRY',(8.8,.05,3.38),.24,gold)

# First-floor central circulation: a framed runner and a visual axis from entrance to stair.
cube('PHQ_AxisRunner',(0,-4.0,.20),(1.35,6.7,.035),wall,.012)
for y in (-9,-7,-5,-3,-1,1): cube('PHQ_AxisGlow',(0,y,.245),(1.05,.018,.018),cyan,.004)

# High-end booth wall along west side.
for i,y in enumerate((-1.0,2.0,5.0)):
    cube(f'PHQ_BoothBack_{i}',(-13.6,y,1.35),(1.25,.95,.85),leather,.18)
    cube(f'PHQ_BoothTable_{i}',(-11.9,y,.98),(1.0,.55,.08),wood,.05)
    for x in (-12.8,-11.1): cyl(f'PHQ_BoothLamp_{i}_{x}',(x,y,2.25),.055,.05,cyan,12)

# Statement pendant cluster above first-floor seating (geometry only; visual pass controls real lights).
for i,(x,y,z) in enumerate([(-5,-1.5,3.55),(-2.5,-2.2,3.85),(0,-1.0,3.65),(2.5,-2.2,3.85),(5,-1.5,3.55)]):
    cyl(f'PHQ_Pendant_{i}',(x,y,z),.11,.07,gold,20)
    cyl(f'PHQ_PendantGlow_{i}',(x,y,z-.08),.07,.025,amber if 'VIS_Amber' in bpy.data.materials else cyan,16)

# Pastry/coffee styling props kept light and reusable.
for x in (7.0,8.0,9.0,10.0):
    cyl('PHQ_CupStack',(x,-.55,2.08),.10,.18,glass,12)
for x in (7.3,9.0,10.7):
    cyl('PHQ_PlantPot',(x,-.55,2.15),.14,.18,wood,16)

# Metadata and optimization policy.
sc=bpy.context.scene
sc['mlo_final_cafe_pass']='premium_props_and_first_floor_v1'
sc['mlo_asset_source']='Poly Haven CC0 runtime assets'
sc['mlo_asset_policy']='curated 2K hero props; duplicates share mesh/material data where possible'
sc['mlo_first_floor_status']='complete premium cafe frontage, service counter, seating spine, circulation axis and feature wall'
sc['mlo_completion_target']='Nocturne Cafe two-story premium interior'

meta={}
if os.path.exists(MANIFEST):
    try:
        with open(MANIFEST,'r',encoding='utf-8') as f: meta=json.load(f)
    except Exception: pass
meta['latest_pass']='premium_props_and_first_floor_v1'
meta['asset_provenance']={'provider':'Poly Haven','license':'CC0','runtime_download':True,'assets':asset_stats}
meta['first_floor']='premium cafe finished pass'
meta['completion_stage']='final visual/content pass before game-readiness validation'
with open(MANIFEST,'w',encoding='utf-8') as f: json.dump(meta,f,indent=2)

bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print('FINAL CAFE QUALITY PASS COMPLETE', BLEND)
