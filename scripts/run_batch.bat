@echo off

rem define installation directory
set INSTALL_DIR=C:\OSGeo4W
rem set INSTALL_DIR=C:\Program Files\QGIS 3.36.2\

rem set environment
call "%INSTALL_DIR%\bin\o4w_env.bat"
set QGIS_PATH=%OSGEO4W_ROOT%/apps/qgis-ltr

rem add root directory to python path
set ROOT_PATH=%~dp0\..
set PYTHONPATH=%ROOT_PATH%;%PYTHONPATH%

rem change current directory to smpdepr2d root directory
cd /d %ROOT_PATH%

rem run batch process
python3 %ROOT_PATH%\scripts\run_batch.py %ROOT_PATH%\tests\batch.yaml

rem wait for 5 sec
timeout /t 50