@echo off
call "%~dp0start_studio.bat" --virtual-camera %*
exit /b %errorlevel%
