import os

ROOT = r'D:\first Blender\mlo'
SCRIPTS = os.path.join(ROOT, 'scripts')


def replace(path, old, new):
    with open(path, 'r', encoding='utf-8') as f:
        s = f.read()
    if old not in s:
        return False
    s = s.replace(old, new)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(s)
    print('PATCHED', os.path.basename(path))
    return True

# Blender 5.2 removed Mesh.use_auto_smooth. The old assignment is unnecessary.
replace(
    os.path.join(SCRIPTS, 'optimize_mlo.py'),
    "        obj.data.use_auto_smooth = False if hasattr(obj.data, 'use_auto_smooth') else getattr(obj.data, 'use_auto_smooth', False)\n",
    "        # Blender 5.2 removed Mesh.use_auto_smooth; geometry is already handled by modifiers.\n"
)

# The access pass has legacy 5-item seat tuples where the room string is passed as yaw.
# Normalize that legacy form so the rotation assignment always receives a number.
replace(
    os.path.join(SCRIPTS, 'usability_and_access_pass.py'),
    "def sit(n,x,y,z=.46,yaw=0,room='cafe'):\n    o=bpy.data.objects.new(n,None);",
    "def sit(n,x,y,z=.46,yaw=0,room='cafe'):\n    if isinstance(yaw, str):\n        room = yaw\n        yaw = 0.0\n        if z == 0: z = .46\n    o=bpy.data.objects.new(n,None);"
)

# The reference rebuild used the old generic name 'white' for the kitchen tiles.
# The intended light material in this reference palette is ivory.
replace(
    os.path.join(SCRIPTS, 'fusion_feast_reference_rebuild.py'),
    ",white,.002,c=KITCH)",
    ",ivory,.002,c=KITCH)"
)

# The optional external hero-prop download endpoint can disappear. Make that pass
# non-fatal so the reference architecture is still built from procedural assets.
path = os.path.join(SCRIPTS, 'final_cafe_quality_pass.py')
with open(path, 'r', encoding='utf-8') as f:
    s = f.read()
if 'HTTPError' not in s:
    s = s.replace('import bpy, os, json, urllib.request, zipfile, io', 'import bpy, os, json, urllib.request, zipfile, io\nfrom urllib.error import HTTPError')
    s = s.replace(
        '        path,res=download_asset(asset_id)\n',
        '        try:\n            path,res=download_asset(asset_id)\n        except (HTTPError, OSError, TimeoutError) as exc:\n            print(f"OPTIONAL HERO PROP SKIPPED: {asset_id}: {exc}")\n            continue\n'
    )
    with open(path, 'w', encoding='utf-8') as f:
        f.write(s)
    print('PATCHED', os.path.basename(path))

print('BLENDER 5.2 BUILD REPAIR COMPLETE')
