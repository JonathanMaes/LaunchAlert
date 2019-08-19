@echo off
cd ..
echo Compile the installer manually. Opening inno setup compiler...
"C:\Program files\Inno Setup 5\ISCC.exe" installer.iss
if errorlevel 1 (
    echo Failed to automatically run Inno Setup Compiler.
    echo You have to compile the installer manually. Opening Inno Setup Compiler...
    installer.iss
    pause
)
cd installer
XCOPY "JonathansBackupper_installer_*.exe" "JonathansBackupper_installer.exe" /C /Y /K
echo Finished.
pause >nul