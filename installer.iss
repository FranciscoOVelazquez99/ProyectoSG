#define MyAppName "SGweb"
#define MyAppVersion "0.21"
#define MyAppPublisher "FranciscoOVelazquez99"
#define MyAppURL "https://github.com/FranciscoOVelazquez99/ProyectoSG.git"
#define MyAppExeName "SGweb.exe"

[Setup]
AppId={{EF55A8D8-521C-4624-A3E1-295F6AACC805}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
InfoAfterFile=C:\Users\Francisco\Desktop\PROYECTOS\ProyectoSG\README.TXT
OutputDir=C:\Users\Francisco\Desktop
OutputBaseFilename={#MyAppName}_Setup
SetupIconFile=C:\Users\Francisco\Downloads\logo.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
DisableFinishedPage=no
DisableProgramGroupPage=yes

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Files]
Source: "C:\Users\Francisco\Desktop\PROYECTOS\ProyectoSG\dist\SGweb.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\Francisco\Desktop\PROYECTOS\ProyectoSG\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\Francisco\Desktop\PROYECTOS\ProyectoSG\requirements.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\Francisco\Desktop\PROYECTOS\ProyectoSG\static\*"; DestDir: "{app}\static"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\Francisco\Desktop\PROYECTOS\ProyectoSG\templates\*"; DestDir: "{app}\templates"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\Francisco\Desktop\PROYECTOS\ProyectoSG\dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\Francisco\Downloads\logo.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Iniciar {#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\logo.ico"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\logo.ico"
Name: "{group}\Detener {#MyAppName}"; Filename: "{app}\stop_app.vbs"; IconFilename: "{sys}\shell32.dll"; IconIndex: 131
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

[Code]
procedure CreateStopScript();
var
  StopContent: String;
  StopFilePath: String;
begin
  StopContent := 'Set objWMIService = GetObject("winmgmts:\\.\root\cimv2")' + #13#10 +
                 'Set colProcessList = objWMIService.ExecQuery("Select * from Win32_Process Where Name = ''SGweb.exe''")' + #13#10 +
                 'For Each objProcess in colProcessList' + #13#10 +
                 '    objProcess.Terminate()' + #13#10 +
                 'Next';
  
  StopFilePath := ExpandConstant('{app}\stop_app.vbs');
  
  SaveStringToFile(StopFilePath, StopContent, False);
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    CreateStopScript();
  end;
end;

[UninstallDelete]
Type: files; Name: "{app}\stop_app.vbs"
