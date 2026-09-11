import os

ROOT = r'D:\first Blender\mlo'
SCRIPTS = os.path.join(ROOT, 'scripts')


def patch(path, replacements):
    with open(path, 'r', encoding='utf-8') as f:
        s = f.read()
    original = s
    for old, new in replacements:
        s = s.replace(old, new)
    if s != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(s)
        print('PATCHED', os.path.basename(path))
    else:
        print('ALREADY PATCHED/NO CHANGE', os.path.basename(path))

# Blender 5.2 removed Mesh.use_auto_smooth. The old assignment is unnecessary.
patch(os.path.join(SCRIPTS, 'optimize_mlo.py'), [
    ("        obj.data.use_auto_smooth = False if hasattr(obj.data, 'use_auto_smooth') else getattr(obj.data, 'use_auto_smooth', False)\n", "        # Blender 5.2 removed Mesh.use_auto_smooth; no replacement is required here.\n")
])

# The access pass has legacy 5-item seat tuples where the room string is passed as yaw.
# Normalize that legacy form so the rotation assignment always receives a number.
patch(os.path.join(SCRIPTS, 'usability_and_access_pass.py'), [
    ("def sit(n,x,y,z=.46,yaw=0,room='cafe'):\n    o=bpy.data.objects.new(n,None);", "def sit(n,x,y,z=.46,yaw=0,room='cafe'):\n    if isinstance(yaw, str):\n        room = yaw\n        yaw = 0.0\n        if z == 0: z = .46\n    o=bpy.data.objects.new(n,None);")
])

# The reference rebuild used the old generic name 'white' for kitchen tiles.
patch(os.path.join(SCRIPTS, 'fusion_feast_reference_rebuild.py'), [
    (",white,.002,c=KITCH)", ",ivory,.002,c=KITCH)")
])

# Poly Haven is optional. A missing/changed endpoint must not abort the restaurant build.
path = os.path.join(SCRIPTS, 'final_cafe_quality_pass.py')
with open(path, 'r', encoding='utf-8') as f:
    s = f.read()
if 'from urllib.error import HTTPError' not in s:
    s = s.replace('import bpy, os, json, math, urllib.request\n', 'import bpy, os, json, math, urllib.request\nfrom urllib.error import HTTPError\n')
old = "for asset_id,cfg in ASSETS.items():\n    path,res=download_asset(asset_id)\n"
new = "for asset_id,cfg in ASSETS.items():\n    try:\n        path,res=download_asset(asset_id)\n    except (HTTPError, OSError, TimeoutError, RuntimeError) as exc:\n        print(f'OPTIONAL HERO PROP SKIPPED: {asset_id}: {exc}')\n        continue\n"
if old in s:
    s = s.replace(old, new)
with open(path, 'w', encoding='utf-8') as f:
    f.write(s)
print('PATCHED optional hero-prop handling')

print('BLENDER 5.2 BUILD REPAIR COMPLETE')
