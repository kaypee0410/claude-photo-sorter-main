@echo off
rem Opens the photo sorter at http://127.0.0.1:8765. Safe to run again: if it's already running it just opens the page.
rem   start.bat          your photos
rem   start.bat --demo   a fake camera roll, to see what it looks like
cd /d "%~dp0"
if not defined PORT set "PORT=8765"
set "URL=http://127.0.0.1:%PORT%/"
if /i "%~1"=="--demo" set "URL=%URL%?demo"
set "PYTHONUTF8=1"
curl.exe -s -o nul "http://127.0.0.1:%PORT%/api/state" >nul 2>nul
if not errorlevel 1 (
  echo Photo sorter is already running.
  start "" "%URL%"
  exit /b 0
)
if not exist ".venv\Scripts\python.exe" (
  call setup.bat || exit /b 1
)
if /i "%~1"=="--demo" if not exist "dashboard\demo\mini\0.jpg" .venv\Scripts\python.exe scripts\demo.py
start "" /b powershell -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Seconds 2; Start-Process '%URL%'"
.venv\Scripts\python.exe scripts\server.py
