@echo off
setlocal
cd /d "D:\first Blender"
if not exist "D:\blender.exe" exit /b 1
if not exist "D:\first Blender\mlo\output" mkdir "D:\first Blender\mlo\output"

echo [1/12] BUILD BASE ARCHITECTURE
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\build_mlo.py"
if errorlevel 1 exit /b 1
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\validate_mlo.py"
if errorlevel 1 exit /b 1

echo [2/12] OPTIMIZE BASE
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\optimize_mlo.py"
if errorlevel 1 exit /b 1
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\validate_mlo.py"
if errorlevel 1 exit /b 1

echo [3/12] EXISTING DETAIL
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\enhance_mlo.py"
if errorlevel 1 exit /b 1
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\validate_mlo.py"
if errorlevel 1 exit /b 1

echo [4/12] PREMIUM ARCHITECTURE
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\premium_detail_pass.py"
if errorlevel 1 exit /b 1
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\validate_mlo.py"
if errorlevel 1 exit /b 1

echo [5/12] TWO-STORY EXPANSION
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\expansion_pass.py"
if errorlevel 1 exit /b 1
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\validate_mlo.py"
if errorlevel 1 exit /b 1

echo [6/12] CURATED FREE HERO PROPS
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\final_cafe_quality_pass.py"
if errorlevel 1 exit /b 1
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\validate_mlo.py"
if errorlevel 1 exit /b 1

echo [7/12] ACCESS + ROOMS + LOCKABLE DOORS + SITTING
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\usability_and_access_pass.py"
if errorlevel 1 exit /b 1
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\validate_mlo.py"
if errorlevel 1 exit /b 1

echo [8/12] BASE COLOR + LIGHTING
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\visual_pass.py"
if errorlevel 1 exit /b 1
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\validate_mlo.py"
if errorlevel 1 exit /b 1

echo [9/12] PALM HOUSE RESTAURANT REDESIGN
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\palm_restaurant_quality_pass.py"
if errorlevel 1 exit /b 1
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\validate_mlo.py"
if errorlevel 1 exit /b 1

echo [10/12] COLORFUL MATERIAL VIEWPORT
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\viewport_setup.py"
if errorlevel 1 exit /b 1
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\validate_mlo.py"
if errorlevel 1 exit /b 1

echo [11/12] OUTPUT CHECK
if not exist "D:\first Blender\mlo\output\Nocturne_Lounge_MLO.blend" exit /b 1
if not exist "D:\first Blender\mlo\output\mlo_showcase.png" exit /b 1
if not exist "D:\first Blender\mlo\output\mlo_manifest.json" exit /b 1

echo [12/12] PALM HOUSE BUILD SUCCESS
exit /b 0
