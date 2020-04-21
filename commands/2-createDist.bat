@echo off
cd ../source
pyinstaller main.spec
rmdir "../dist" /S /Q
echo d | XCOPY /C /Y /K /S /Q "dist/main" "../dist"
rmdir dist /S /Q
rmdir build /S /Q
pause