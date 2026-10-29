@echo off
setlocal
pushd "%~dp0"

set "VENV_DIR=.venv"
set "VENV_PY=%VENV_DIR%\Scripts\python.exe"

if exist "%VENV_PY%" goto :run

echo [GhostCam Studio] Creating local Python virtual environment...
where py >nul 2>nul
if not errorlevel 1 (
  py -3 -m venv "%VENV_DIR%"
) else (
  python -m venv "%VENV_DIR%"
)
if errorlevel 1 goto :error

:run
"%VENV_PY%" -c "import cv2, mediapipe, numpy, pyvirtualcam, pygame" >nul 2>nul
if errorlevel 1 (
  echo [GhostCam Studio] Installing dependencies...
  "%VENV_PY%" -m pip install --upgrade pip
  if errorlevel 1 goto :error
  "%VENV_PY%" -m pip install -r "requirements.txt"
  if errorlevel 1 goto :error
)

echo [GhostCam Studio] Launching studio...
"%VENV_PY%" "main.py" %*
if errorlevel 1 goto :error
popd
exit /b 0

:error
echo.
echo Unable to launch GhostCam Studio. Check README.md for troubleshooting.
popd
pause
exit /b 1
