import bpy, os, json

ROOT = r'D:\first Blender\mlo'
OUT = os.path.join(ROOT, 'output')
BLEND = os.path.join(OUT, 'Nocturne_Lounge_MLO.blend')
MANIFEST = os.path.join(OUT, 'mlo_manifest.json')

if not os.path.exists(BLEND):
    raise RuntimeError('viewport_setup: missing MLO blend')

bpy.ops.wm.open_mainfile(filepath=BLEND)

# Make the material colors visible even when the user opens the .blend in a
# normal Solid viewport. This also switches saved 3D viewports to Material
# Preview so the checkpoint is immediately inspectable.
for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    bs = mat.node_tree.nodes.get('Principled BSDF')
    if not bs:
        continue
    base = bs.inputs.get('Base Color')
    if base:
        mat.diffuse_color = base.default_value

for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            shading = area.spaces.active.shading
            shading.type = 'MATERIAL'
            shading.color_type = 'MATERIAL'
            shading.show_shadows = True
            shading.show_cavity = True
            try:
                shading.cavity_type = 'BOTH'
            except Exception:
                pass

scene = bpy.context.scene
scene['mlo_viewport']='material_preview'
scene['mlo_colors_visible']=True
scene['mlo_checkpoint']='color_visibility_v1'

meta = {}
if os.path.exists(MANIFEST):
    try:
        with open(MANIFEST, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except Exception:
        pass
meta['viewport'] = {'mode':'MATERIAL','colors_visible':True}
meta['latest_pass'] = 'color_visibility_v1'
with open(MANIFEST, 'w', encoding='utf-8') as f:
    json.dump(meta, f, indent=2)

bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print('VIEWPORT COLOR SETUP COMPLETE:', BLEND)
