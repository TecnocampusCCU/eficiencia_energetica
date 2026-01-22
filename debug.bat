@echo off
set MYDIR=%cd%
for %%f in (%MYDIR%) do set directory=%%~nxf

set QGIS_PATH=C:\Program Files\QGIS 3.28.15
CALL "%QGIS_PATH%\bin\o4w_env.bat"

@echo on
cmd /c "pyrcc5 -o resources.py resources.qrc"
cmd /c "rmdir /S /Q "%APPDATA%"\QGIS\QGIS3\profiles\default\python\plugins\%directory%"
cmd /c "xcopy ..\%directory% "%APPDATA%"\QGIS\QGIS3\profiles\default\python\plugins\%directory% /E /Q /I /Y"
exit