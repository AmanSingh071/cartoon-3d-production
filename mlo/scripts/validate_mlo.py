import bpy, os, json, sys

ROOT = r'D:\first Blender\mlo'
OUT = os.path.join(ROOT, 'output')
BLEND = os.path.join(OUT, 'Nocturne_Lounge_MLO.blend')
MANIFEST = os.path.join(OUT, 'mlo_manifest.json')

if not os.path.exists(BLEND):
    raise RuntimeError('MLO validation failed: blend file does not exist')

bpy.ops.wm.open_mainfile(filepath=BLEND)
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
mesh_names = {o.name for o in meshes}
required = {'Floor', 'Wall_Back', 'Wall_Left', 'Wall_Right', 'Stage', 'BarCounter', 'FeatureWall'}
missing = sorted(required - mesh_names)

if len(meshes) < 40:
    raise RuntimeError(f'MLO validation failed: only {len(meshes)} mesh objects found; expected a complete interior')
if missing:
    raise RuntimeError('MLO validation failed: missing core geometry: ' + ', '.join(missing))

bbox_objects = [o for o in meshes if o.name in required]
mins = [min(o.matrix_world.translation[i] for o in bbox_objects) for i in range(3)]
maxs = [max(o.matrix_world.translation[i] for o in bbox_objects) for i in range(3)]
if maxs[0] - mins[0] < 10 or maxs[1] - mins[1] < 10:
    raise RuntimeError('MLO validation failed: geometry footprint is implausibly small')

scene = bpy.context.scene
scene['mlo_validation'] = 'PASS'
scene['mlo_mesh_object_count'] = len(meshes)
scene['mlo_core_geometry_present'] = True
bpy.ops.wm.save_as_mainfile(filepath=BLEND)

meta = {}
if os.path.exists(MANIFEST):
    try:
        with open(MANIFEST, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except Exception:
        pass
meta['validation'] = {'status': 'PASS', 'mesh_objects': len(meshes), 'core_geometry': True}
meta['status'] = 'validated complete interior geometry'
with open(MANIFEST, 'w', encoding='utf-8') as f:
    json.dump(meta, f, indent=2)

print(f'MLO VALIDATION PASS: {len(meshes)} mesh objects; core architecture present')
