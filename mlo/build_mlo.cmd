@echo off
setlocal
cd /d "D:\first Blender"
if not exist "D:\blender.exe" (
  echo Blender not found at D:\blender.exe
  exit /b 1
)
if not exist "D:\first Blender\mlo\output" mkdir "D:\first Blender\mlo\output"
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\build_mlo.py"
if errorlevel 1 exit /b 1
if not exist "D:\first Blender\mlo\output\Nocturne_Lounge_MLO.blend" exit /b 1
if not exist "D:\first Blender\mlo\output\mlo_showcase.png" exit /b 1
echo MLO build complete.
