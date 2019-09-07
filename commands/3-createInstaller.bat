@echo off
cd ..
echo Compile the installer manually. Opening inno setup compiler...
"C:\Program files\Inno Setup 5 (x86)\ISCC.exe" installer.iss
if errorlevel 1 (
    echo Failed to automatically run Inno Setup Compiler.
    echo You have to compile the installer manually. Opening Inno Setup Compiler...
    installer.iss
    pause
)
cd installer
echo f | XCOPY "JonathansLaunchAlert_installer_*.exe" "JonathansLaunchAlert_installer.exe" /C /Y /K

set /p var=<"../source/changelog.txt"
echo %var% > "../installer/version.txt"

echo Finished.
pause >nul