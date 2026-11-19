@echo off
rem One-time setup on Windows: checks Python and ffmpeg, installs the Python packages into .venv\
cd /d "%~dp0"
set "PY="
py -3 --version >nul 2>nul && set "PY=py -3"
if not defined PY python --version >nul 2>nul && set "PY=python"
if not defined PY (
  echo Python 3 is missing. Install it with:  winget install Python.Python.3.12
  echo Then close this window, open a new one and run setup.bat again.
  exit /b 1
)
where ffmpeg >nul 2>nul || (
  echo Note: ffmpeg is not installed, so videos get grey previews.
  echo       Install it with:  winget install Gyan.FFmpeg   then open a new terminal.
)
%PY% -m venv .venv || exit /b 1
.venv\Scripts\python.exe -m pip install -q --upgrade pip
.venv\Scripts\python.exe -m pip install -q -r requirements.txt || exit /b 1
echo Setup done. Next: start.bat   (or start.bat --demo to see the demo)
exit /b 0
