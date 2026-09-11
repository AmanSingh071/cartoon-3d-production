@echo off
setlocal
cd /d "D:\first Blender"
if not exist "D:\blender.exe" exit /b 1
if not exist "D:\first Blender\mlo\output" mkdir "D:\first Blender\mlo\output"

echo [1/9] BUILD BASE ARCHITECTURE
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\build_mlo.py"
if errorlevel 1 exit /b 1
if not exist "D:\first Blender\mlo\output\Nocturne_Lounge_MLO.blend" exit /b 1
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\validate_mlo.py"
if errorlevel 1 exit /b 1

echo [2/9] OPTIMIZE BASE MLO
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\optimize_mlo.py"
if errorlevel 1 exit /b 1
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\validate_mlo.py"
if errorlevel 1 exit /b 1

echo [3/9] ADD EXISTING DETAIL PASS
if exist "D:\first Blender\mlo\scripts\enhance_mlo.py" (
  "D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\enhance_mlo.py"
  if errorlevel 1 exit /b 1
)
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\validate_mlo.py"
if errorlevel 1 exit /b 1

echo [4/9] ADD PREMIUM ARCHITECTURAL DETAIL
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\premium_detail_pass.py"
if errorlevel 1 exit /b 1
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\validate_mlo.py"
if errorlevel 1 exit /b 1

echo [5/9] EXPAND TO TWO-STORY PREMIUM CAFE
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\expansion_pass.py"
if errorlevel 1 exit /b 1
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\validate_mlo.py"
if errorlevel 1 exit /b 1

echo [6/9] APPLY COLOR + LIGHTING
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\visual_pass.py"
if errorlevel 1 exit /b 1
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\validate_mlo.py"
if errorlevel 1 exit /b 1

echo [7/9] SAVE COLORFUL VIEWPORT CHECKPOINT
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\viewport_setup.py"
if errorlevel 1 exit /b 1
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\validate_mlo.py"
if errorlevel 1 exit /b 1

echo [8/9] FINAL OUTPUT CHECK
if not exist "D:\first Blender\mlo\output\Nocturne_Lounge_MLO.blend" exit /b 1
if not exist "D:\first Blender\mlo\output\mlo_showcase.png" exit /b 1
if not exist "D:\first Blender\mlo\output\mlo_manifest.json" exit /b 1

echo [9/9] MLO BUILD SUCCESS - TWO-STORY CAFE EXPANSION + DETAIL + COLOR CHECKPOINT VALIDATED
exit /b 0
