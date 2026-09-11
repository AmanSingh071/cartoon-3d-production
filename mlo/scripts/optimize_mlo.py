import bpy, os, json

ROOT = r'D:\first Blender\mlo'
OUT = os.path.join(ROOT, 'output')
BLEND = os.path.join(OUT, 'Nocturne_Lounge_MLO.blend')
MANIFEST = os.path.join(OUT, 'mlo_manifest.json')

if not os.path.exists(BLEND):
    raise FileNotFoundError(BLEND)

bpy.ops.wm.open_mainfile(filepath=BLEND)

# Keep the generated scene visually intact while reducing modifier overhead.
bevel_count = 0
for obj in bpy.data.objects:
    for mod in obj.modifiers:
        if mod.type == 'BEVEL':
            mod.segments = min(getattr(mod, 'segments', 2), 2)
            bevel_count += 1

# Mark reusable/game-ready assets for downstream Sollumz/CodeWalker export tooling.
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        obj.data.use_auto_smooth = False if hasattr(obj.data, 'use_auto_smooth') else getattr(obj.data, 'use_auto_smooth', False)
        obj['mlo_game_asset'] = True
        obj['mlo_export_ready'] = True

# Organize objects into purpose collections without duplicating geometry.
root_col = bpy.data.collections.get('MLO_Geometry')
if root_col:
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and obj.name not in root_col.objects:
            try:
                root_col.objects.link(obj)
            except RuntimeError:
                pass

# Scene-level optimization metadata for the next export pass.
scene = bpy.context.scene
scene['mlo_optimization'] = 'bevel_segments_capped_at_2; reusable_mesh_assets_marked; export_metadata_added'
scene['mlo_target'] = 'FiveM'
scene['mlo_export_pipeline'] = 'Sollumz/CodeWalker'

# Purge orphan datablocks left by iterative development.
for _ in range(2):
    try:
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
    except Exception:
        pass

bpy.ops.wm.save_as_mainfile(filepath=BLEND)

meta = {}
if os.path.exists(MANIFEST):
    try:
        with open(MANIFEST, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except Exception:
        meta = {}
meta['status'] = 'optimized blockout + detailed asset pass'
meta['optimization'] = {
    'bevel_segments_capped': 2,
    'game_assets_marked': True,
    'orphan_cleanup': True,
    'export_ready_metadata': True
}
with open(MANIFEST, 'w', encoding='utf-8') as f:
    json.dump(meta, f, indent=2)

print('MLO OPTIMIZATION COMPLETE:', BLEND)
