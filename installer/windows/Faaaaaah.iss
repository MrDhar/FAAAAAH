#define MyAppName "Faaaaaah"
#define MyAppVersion "1.0.1"
#define MyAppPublisher "Faaaaaah"
#define MyAppExeName "Faaaaaah.exe"

[Setup]
AppId={{6F1D2A3B-4C5E-4F60-8A7B-9C0D1E2F3A4B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL=https://github.com/MrDhar/FAAAAAH
AppSupportURL=https://github.com/MrDhar/FAAAAAH/issues
DefaultDirName={autopf}\Faaaaaah
DefaultGroupName=Faaaaaah
OutputDir=..\..\dist-installer
OutputBaseFilename=Faaaaaah-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
WizardImageFile=wizard-side.bmp
WizardSmallImageFile=wizard-small.bmp
WizardImageStretch=no
SetupIconFile=..\..\assets\Faaaaaah.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
DisableProgramGroupPage=yes
Uninstallable=yes

[Files]
Source: "..\..\dist\Faaaaaah\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{group}\Faaaaaah"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\Faaaaaah"; Filename: "{app}\{#MyAppExeName}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch Faaaaaah — make your keyboard speak"; Flags: nowait postinstall skipifsilent

[Messages]
WelcomeLabel1=Welcome to Faaaaaah!
WelcomeLabel2=You're about to give every key a voice.\n\nThe tiny sound. The ridiculous idea. The surprisingly satisfying result.\n\nLet's install it.
SelectDirLabel3=Choose where the Faaaaaah magic should live:
ReadyLabel1=Everything is ready.
ReadyLabel2=Faaaaaah will now be installed with its mascot, sounds and keyboard engine.
FinishedHeadingLabel=Faaaaaah is ready.
FinishedLabelNoIcons=Installation complete. Your keyboard has officially become a little louder.
FinishedLabel=Installation complete. Launch Faaaaaah and let the chaos begin.

[Code]
procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = wpInstalling then
    WizardForm.StatusLabel.Caption := 'Unleashing the Faaaaaah...';
  if CurPageID = wpFinished then
    WizardForm.StatusLabel.Caption := 'The keyboard is ready.';
end;
