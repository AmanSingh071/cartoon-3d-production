@echo off
setlocal
cd /d "D:\first Blender"
if not exist "D:\blender.exe" (
  echo Blender not found at D:\blender.exe
  exit /b 1
)
if not exist "D:\first Blender\mlo\output" mkdir "D:\first Blender\mlo\output"

echo [1/8] BUILD BASE ARCHITECTURE
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\build_mlo.py"
if errorlevel 1 exit /b 1
if not exist "D:\first Blender\mlo\output\Nocturne_Lounge_MLO.blend" exit /b 1

"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\validate_mlo.py"
if errorlevel 1 exit /b 1

echo [2/8] OPTIMIZE BASE MLO
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\optimize_mlo.py"
if errorlevel 1 exit /b 1
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\validate_mlo.py"
if errorlevel 1 exit /b 1

echo [3/8] ADD EXISTING DETAIL PASS
if exist "D:\first Blender\mlo\scripts\enhance_mlo.py" (
  "D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\enhance_mlo.py"
  if errorlevel 1 exit /b 1
)
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\validate_mlo.py"
if errorlevel 1 exit /b 1

echo [4/8] ADD PREMIUM ARCHITECTURAL DETAIL
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\premium_detail_pass.py"
if errorlevel 1 exit /b 1
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\validate_mlo.py"
if errorlevel 1 exit /b 1

echo [5/8] APPLY COLOR + LIGHTING
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\visual_pass.py"
if errorlevel 1 exit /b 1
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\validate_mlo.py"
if errorlevel 1 exit /b 1

echo [6/8] SAVE COLORFUL VIEWPORT CHECKPOINT
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\viewport_setup.py"
if errorlevel 1 exit /b 1
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\validate_mlo.py"
if errorlevel 1 exit /b 1

echo [7/8] FINAL OUTPUT CHECK
if not exist "D:\first Blender\mlo\output\Nocturne_Lounge_MLO.blend" exit /b 1
if not exist "D:\first Blender\mlo\output\mlo_showcase.png" exit /b 1
if not exist "D:\first Blender\mlo\output\mlo_manifest.json" exit /b 1

echo [8/8] MLO BUILD SUCCESS - PREMIUM DETAIL + COLOR CHECKPOINT VALIDATED
exit /b 0
