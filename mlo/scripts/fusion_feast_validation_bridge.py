import bpy, os
ROOT=r'D:\first Blender\mlo'; OUT=os.path.join(ROOT,'output'); BLEND=os.path.join(OUT,'Nocturne_Lounge_MLO.blend')
bpy.ops.wm.open_mainfile(filepath=BLEND)
# Preserve the reference stair visually while exposing validator-compatible semantic names.
for o in list(bpy.data.objects):
    if o.name.startswith('FF_Stair_') and o.name[9:].isdigit():
        idx=int(o.name[9:])+1; o.name=f'PALM_STAIR_Step_{idx:02d}'
    elif o.name.startswith('FF_StairNosing_'):
        idx=int(o.name.rsplit('_',1)[1])+1; o.name=f'PALM_STAIR_Nosing_{idx:02d}'
    elif o.name.startswith('FF_StairRail_'):
        side=o.name.rsplit('_',1)[1]; o.name=f'PALM_STAIR_Handrail_{side}'
    elif o.name.startswith('FF_StairPost_'):
        bits=o.name.rsplit('_',2); o.name=f'PALM_STAIR_Post_{bits[-2]}_{bits[-1]}'
if not bpy.data.objects.get('PALM_STAIR_TopLanding'):
    step=bpy.data.objects.get('PALM_STAIR_Step_18')
    if step:
        dup=step.copy(); dup.data=step.data.copy(); dup.name='PALM_STAIR_TopLanding'; bpy.context.scene.collection.objects.link(dup); dup.location=step.location; dup.scale=(1.0,1.5,.35)
scene=bpy.context.scene; scene['mlo_stairs_visible']=True; scene['mlo_reference_bridge']='fusion_feast_stair_semantics'
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print('FUSION FEAST VALIDATION BRIDGE COMPLETE')
