@echo off
rem Windows: double-click to install. Options: install.cmd -Copy  or  install.cmd -Uninstall
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\install.ps1" %*
pause
