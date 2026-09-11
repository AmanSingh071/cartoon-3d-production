@echo off
setlocal
cd /d "D:\first Blender"
if not exist "D:\blender.exe" exit /b 1
if not exist "D:\first Blender\mlo\output" mkdir "D:\first Blender\mlo\output"

echo [1/14] BUILD BASE ARCHITECTURE
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\build_mlo.py"
if errorlevel 1 exit /b 1
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\validate_mlo.py"
if errorlevel 1 exit /b 1

echo [2/14] OPTIMIZE BASE
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\optimize_mlo.py"
if errorlevel 1 exit /b 1
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\validate_mlo.py"
if errorlevel 1 exit /b 1

echo [3/14] EXISTING DETAIL
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\enhance_mlo.py"
if errorlevel 1 exit /b 1
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\validate_mlo.py"
if errorlevel 1 exit /b 1

echo [4/14] PREMIUM ARCHITECTURE
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\premium_detail_pass.py"
if errorlevel 1 exit /b 1
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\validate_mlo.py"
if errorlevel 1 exit /b 1

echo [5/14] TWO-STORY EXPANSION
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\expansion_pass.py"
if errorlevel 1 exit /b 1
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\validate_mlo.py"
if errorlevel 1 exit /b 1

echo [6/14] CURATED FREE HERO PROPS
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\final_cafe_quality_pass.py"
if errorlevel 1 exit /b 1
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\validate_mlo.py"
if errorlevel 1 exit /b 1

echo [7/14] ACCESS + ROOMS + LOCKABLE DOORS + SITTING
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\usability_and_access_pass.py"
if errorlevel 1 exit /b 1
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\validate_mlo.py"
if errorlevel 1 exit /b 1

echo [8/14] BASE COLOR + LIGHTING
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\visual_pass.py"
if errorlevel 1 exit /b 1
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\validate_mlo.py"
if errorlevel 1 exit /b 1

echo [9/14] PALM HOUSE REDESIGN BASE
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\palm_restaurant_quality_pass.py"
if errorlevel 1 exit /b 1
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\validate_mlo.py"
if errorlevel 1 exit /b 1

echo [10/14] FUSION FEAST VIDEO REFERENCE RECREATION
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\fusion_feast_reference_pass.py"
if errorlevel 1 exit /b 1

echo [11/14] REFERENCE STAIR VALIDATION BRIDGE
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\fusion_feast_validation_bridge.py"
if errorlevel 1 exit /b 1
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\validate_mlo.py"
if errorlevel 1 exit /b 1

echo [12/14] COLORFUL MATERIAL VIEWPORT
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\viewport_setup.py"
if errorlevel 1 exit /b 1
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\validate_mlo.py"
if errorlevel 1 exit /b 1

echo [13/14] OUTPUT CHECK
if not exist "D:\first Blender\mlo\output\Nocturne_Lounge_MLO.blend" exit /b 1
if not exist "D:\first Blender\mlo\output\mlo_showcase.png" exit /b 1
if not exist "D:\first Blender\mlo\output\mlo_manifest.json" exit /b 1

echo [14/14] FUSION FEAST REFERENCE BUILD SUCCESS
exit /b 0
