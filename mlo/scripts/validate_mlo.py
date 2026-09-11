import bpy, os, json

ROOT=r'D:\first Blender\mlo'; OUT=os.path.join(ROOT,'output'); BLEND=os.path.join(OUT,'Nocturne_Lounge_MLO.blend'); MANIFEST=os.path.join(OUT,'mlo_manifest.json')
if not os.path.exists(BLEND): raise RuntimeError('MLO validation failed: blend file does not exist')
bpy.ops.wm.open_mainfile(filepath=BLEND)
meshes=[o for o in bpy.data.objects if o.type=='MESH']; mesh_names={o.name for o in meshes}
required={'Floor','Wall_Back','Wall_Left','Wall_Right','BarCounter','FeatureWall'}; missing=sorted(required-mesh_names)
if len(meshes)<40: raise RuntimeError(f'MLO validation failed: only {len(meshes)} mesh objects found; expected a complete interior')
if missing: raise RuntimeError('MLO validation failed: missing core geometry: '+', '.join(missing))
bbox=[o for o in meshes if o.name in required]; mins=[min(o.matrix_world.translation[i] for o in bbox) for i in range(3)]; maxs=[max(o.matrix_world.translation[i] for o in bbox) for i in range(3)]
if maxs[0]-mins[0]<10 or maxs[1]-mins[1]<10: raise RuntimeError('MLO validation failed: geometry footprint is implausibly small')

scene=bpy.context.scene
access_ready=bool(scene.get('mlo_access_pass'))
access_report={}
if access_ready:
    door_leaves=[o for o in meshes if o.name.startswith('DOOR_') and o.name.endswith('_Leaf')]
    lock_objs=[o for o in meshes if o.name.startswith('DOOR_') and o.name.endswith('_Lock') and o.get('lockable')]
    stair_steps=[o for o in meshes if o.name.startswith('STAIR_Step_') or o.name.startswith('PALM_STAIR_Step_')]
    stair_landing=bpy.data.objects.get('STAIR_TopLanding') or bpy.data.objects.get('PALM_STAIR_TopLanding')
    seats=[o for o in bpy.data.objects if o.type=='EMPTY' and o.get('sittable')]
    if len(door_leaves)<6: raise RuntimeError(f'MLO access validation failed: only {len(door_leaves)} door leaves; expected entrance + room doors')
    if len(lock_objs)<6: raise RuntimeError(f'MLO access validation failed: only {len(lock_objs)} lockable door controls')
    if len(stair_steps)<18 or stair_landing is None: raise RuntimeError('MLO access validation failed: complete visible stair and top landing are missing')
    if max((o.matrix_world.translation.z for o in stair_steps),default=0)<3.8: raise RuntimeError('MLO access validation failed: stair does not reach the second-floor level')
    if len(seats)<12: raise RuntimeError(f'MLO seating validation failed: only {len(seats)} sittable anchors')
    if not scene.get('mlo_entrance_clear') or not scene.get('mlo_doors_lockable') or not scene.get('mlo_stairs_visible'): raise RuntimeError('MLO access validation failed: required access metadata is incomplete')
    access_report={'status':'PASS','door_leaves':len(door_leaves),'lockable_doors':len(lock_objs),'stair_steps':len(stair_steps),'sittable_anchors':len(seats),'entrance_clear':True,'rooms_enclosed_and_signed':bool(scene.get('mlo_rooms_enclosed_and_signed'))}

scene['mlo_validation']='PASS'; scene['mlo_mesh_object_count']=len(meshes); scene['mlo_core_geometry_present']=True
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
meta={}
if os.path.exists(MANIFEST):
    try:
        with open(MANIFEST,'r',encoding='utf-8') as f: meta=json.load(f)
    except Exception: pass
meta['validation']={'status':'PASS','mesh_objects':len(meshes),'core_geometry':True,'accessibility':access_report}
meta['status']='validated complete interior geometry'+(' + access/usability checks' if access_ready else '')
with open(MANIFEST,'w',encoding='utf-8') as f: json.dump(meta,f,indent=2)
print(f'MLO VALIDATION PASS: {len(meshes)} mesh objects; core architecture present; access_ready={access_ready}')
