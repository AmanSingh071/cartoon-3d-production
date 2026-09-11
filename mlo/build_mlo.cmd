@echo off
setlocal
cd /d "D:\first Blender"
if not exist "D:\blender.exe" (
  echo Blender not found at D:\blender.exe
  exit /b 1
)
if not exist "D:\first Blender\mlo\output" mkdir "D:\first Blender\mlo\output"

echo [1/6] BUILD BASE ARCHITECTURE
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\build_mlo.py"
if errorlevel 1 exit /b 1
if not exist "D:\first Blender\mlo\output\Nocturne_Lounge_MLO.blend" exit /b 1

echo [2/6] OPTIMIZE BASE MLO
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\optimize_mlo.py"
if errorlevel 1 exit /b 1

"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\validate_mlo.py"
if errorlevel 1 exit /b 1

echo [3/6] ADD DETAIL WITHOUT REPLACING ARCHITECTURE
if exist "D:\first Blender\mlo\scripts\enhance_mlo.py" (
  "D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\enhance_mlo.py"
  if errorlevel 1 exit /b 1
)
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\validate_mlo.py"
if errorlevel 1 exit /b 1

echo [4/6] APPLY COLOR + LIGHTING
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\visual_pass.py"
if errorlevel 1 exit /b 1
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\validate_mlo.py"
if errorlevel 1 exit /b 1

echo [5/6] FINAL OUTPUT CHECK
if not exist "D:\first Blender\mlo\output\Nocturne_Lounge_MLO.blend" exit /b 1
if not exist "D:\first Blender\mlo\output\mlo_showcase.png" exit /b 1
if not exist "D:\first Blender\mlo\output\mlo_manifest.json" exit /b 1

echo [6/6] MLO BUILD SUCCESS - REAL INTERIOR VALIDATED
exit /b 0
