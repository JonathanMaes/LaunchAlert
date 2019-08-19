@echo off
cd ../source
pyinstaller main.spec --upx-dir=..\upx-3.95-win64
echo d | XCOPY /C /Y /K /S /Q "dist/main" "../dist"
rmdir dist /S /Q
rmdir build /S /Q
pause