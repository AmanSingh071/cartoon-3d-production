@echo off
setlocal
cd /d "D:\first Blender"

echo === SYNC MLO PRODUCTION ===
git fetch origin mlo-production
if errorlevel 1 exit /b 1
git checkout mlo-production
if errorlevel 1 exit /b 1
git reset --hard origin/mlo-production
if errorlevel 1 exit /b 1

echo === CLEAN OUTPUT ===
if not exist "D:\first Blender\mlo\output" mkdir "D:\first Blender\mlo\output"
del /f /q "D:\first Blender\mlo\output\Nocturne_Lounge_MLO.blend" 2>nul
del /f /q "D:\first Blender\mlo\output\mlo_showcase.png" 2>nul
del /f /q "D:\first Blender\mlo\output\mlo_manifest.json" 2>nul

echo === BUILD COMPLETE MLO ===
call "D:\first Blender\mlo\build_mlo.cmd"
if errorlevel 1 (
  echo BUILD FAILED - NOT OPENING OLD FILE
  exit /b 1
)

echo === FINAL GEOMETRY VALIDATION ===
"D:\blender.exe" --background --python "D:\first Blender\mlo\scripts\validate_mlo.py"
if errorlevel 1 (
  echo VALIDATION FAILED - NOT OPENING FILE
  exit /b 1
)

echo === OPENING VALIDATED MLO ===
"D:\blender.exe" "D:\first Blender\mlo\output\Nocturne_Lounge_MLO.blend"
