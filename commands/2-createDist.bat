@echo off
cd ../source
pyinstaller main.spec
XCOPY "dist/main" "../dist" /C /Y /K /S /Q
rmdir dist /S /Q
rmdir build /S /Q
pause