#define ApplicationVersion GetFileVersion('dist/jonathanslaunchnotifications.exe')

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{A792DC76-797B-4CDB-8AE3-7487B01189C0}
AppName=Jonathan's Launch Alert
AppVersion={#ApplicationVersion}
VersionInfoVersion={#ApplicationVersion}
AppPublisher=OrOrg Development, Inc.
AppPublisherURL=https://github.com/JonathanMaes/LaunchAlert
AppSupportURL=https://github.com/JonathanMaes/LaunchAlert/issues
AppUpdatesURL=https://github.com/JonathanMaes/LaunchAlert/releases
DefaultDirName={pf}\Jonathan's Launch Alert
DefaultGroupName=Jonathan's Launch Alert
AllowNoIcons=yes
LicenseFile=LICENSE
OutputDir=installer
OutputBaseFilename="JonathansLaunchAlert_installer_{#ApplicationVersion}"
SetupIconFile=dist\icon.ico
Compression=lzma
SolidCompression=yes       
DisableDirPage=auto
DisableProgramGroupPage=auto
PrivilegesRequired=admin
CloseApplications=force

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\jonathanslaunchnotifications.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\Jonathan's Launch Alert"; Filename: "{app}\jonathanslaunchnotifications.exe"
Name: "{commondesktop}\Jonathan's Launch Alert"; Filename: "{app}\jonathanslaunchnotifications.exe"; Tasks: desktopicon
Name: "{commonstartup}\Jonathan's Launch Alert"; Filename: "{app}\jonathanslaunchnotifications.exe"; Parameters: "noGUI"

[Run]
Filename: "{app}\jonathanslaunchnotifications.exe"; Description: "{cm:LaunchProgram,Jonathan's Launch Alert}"; Flags: nowait postinstall skipifsilent

;[UninstallDelete]
;Type: files; Name: "{userappdata}\Jonathan's Launch Alert\options.json"