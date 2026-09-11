# Nocturne Lounge — Live Production Progress

This file is the single source of truth for the MLO production checkpoints.

## Current status
**Stage 1 — Spatial blockout + first detailed asset pass**

Progress: **10%**

### Completed
- [x] 28m × 22m × 4.2m lounge shell
- [x] Floor, walls, ceiling structure
- [x] DJ stage and DJ desk
- [x] Bar and back-bar layout
- [x] VIP seating and dining seating
- [x] Feature wall / NOCTURNE signage
- [x] First decorative props
- [x] Initial material palette
- [x] Layered accent lighting
- [x] Showcase camera setup
- [x] Blender showcase render setup

### In production
- [ ] Higher-detail furniture and hero props
- [ ] Additional decorative assets
- [ ] Material refinement / PBR pass
- [ ] Lighting polish
- [ ] Collision meshes
- [ ] LODs and optimization
- [ ] Occlusion / portal planning
- [ ] GTA V asset conversion
- [ ] YTYP / YMAP / YBN setup
- [ ] FiveM resource packaging
- [ ] In-game testing
- [ ] Final bug-fix and optimization pass

## Blender file
The production PC writes the working files to:

`D:\first Blender\mlo\output\Nocturne_Lounge_MLO.blend`

The build script also generates:

`D:\first Blender\mlo\output\mlo_showcase.png`

The existing build command verifies both files after a successful build.

## Checkpoint policy
A preview checkpoint should be produced after each major visual stage. Changes requested from a checkpoint should be applied to the next build rather than being lost in later automation.

## Quality gate
The project is **not considered final** until the Blender asset is converted for GTA V/FiveM, packaged, loaded in-game, visually checked, collision-tested, and optimized.
