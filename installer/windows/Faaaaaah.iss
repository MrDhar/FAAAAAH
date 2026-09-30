#define MyAppName "Faaaaaah"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Faaaaaah"
#define MyAppExeName "Faaaaaah.exe"

[Setup]
AppId={{6F1D2A3B-4C5E-4F60-8A7B-9C0D1E2F3A4B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Faaaaaah
DefaultGroupName=Faaaaaah
OutputDir=..\..\dist-installer
OutputBaseFilename=Faaaaaah-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
SetupIconFile=..\..\assets\Faaaaaah.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest

[Files]
Source: "..\..\dist\Faaaaaah\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{group}\Faaaaaah"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\Faaaaaah"; Filename: "{app}\{#MyAppExeName}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch Faaaaaah"; Flags: nowait postinstall skipifsilent
