[Setup]
AppName=DPI Tintas HP
AppVersion=2.0.0
AppPublisher=DPI Visual
AppPublisherURL=https://dpivisual.com.br
DefaultDirName={autopf}\DPI Tintas HP
DefaultGroupName=DPI Tintas HP
OutputDir=installer
OutputBaseFilename=DPI-Tintas-HP-Setup
Compression=lzma2
SolidCompression=yes
SetupIconFile=src\images\app_icon.ico
UninstallDisplayIcon={app}\DPI-Tintas-HP.exe
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0

[Languages]
Name: "portuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\DPI-Tintas-HP.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "scripts\create_db.py"; DestDir: "{app}\scripts"; Flags: ignoreversion

[Icons]
Name: "{group}\DPI Tintas HP"; Filename: "{app}\DPI-Tintas-HP.exe"
Name: "{group}\{cm:UninstallProgram,DPI Tintas HP}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\DPI Tintas HP"; Filename: "{app}\DPI-Tintas-HP.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\DPI-Tintas-HP.exe"; Description: "{cm:LaunchProgram,DPI Tintas HP}"; Flags: nowait postinstall skipifsilent

[Code]
var
  ConfigWizardPage: TInputQueryWizardPage;

function CreateConfigPage: TInputQueryWizardPage;
begin
  Result := CreateInputQueryPage(wpSelectDir,
    'Configuracao Inicial - v2.0',
    'Configure os precos dos cartuchos de tinta.',
    'Estas configuracoes serao aplicadas ao banco de dados. Voce pode altera-las depois pelo programa. Capacidade padrao: 775ml.');

  Result.Add('Preco Cyan (R$):', False);
  Result.Values[0] := '50.00';

  Result.Add('Preco Magenta (R$):', False);
  Result.Values[1] := '50.00';

  Result.Add('Preco Yellow (R$):', False);
  Result.Values[2] := '50.00';

  Result.Add('Preco Black (R$):', False);
  Result.Values[3] := '50.00';

  Result.Add('Preco Light Cyan (R$):', False);
  Result.Values[4] := '50.00';

  Result.Add('Preco Light Magenta (R$):', False);
  Result.Values[5] := '50.00';

  Result.Add('Preco Opaca (R$):', False);
  Result.Values[6] := '50.00';
end;

function CreateDatabase(ConfigPage: TInputQueryWizardPage): Boolean;
var
  DbPath, Cmd, ConfigPath: String;
  ResultCode: Integer;
begin
  Result := True;
  DbPath := ExpandConstant('{localappdata}\DPI Tintas HP\tintas_controle.db');

  if FileExists(DbPath) then
  begin
    Exit;
  end;

  ConfigPath := ExpandConstant('{tmp}\installer_config.json');
  SaveStringToFile(ConfigPath,
    '{"capacidade_ml": 775.0,' + #13#10 +
    ' "nivel_atual_ml": 775.0,' + #13#10 +
    ' "precos": {' + #13#10 +
    '   "C": ' + ConfigPage.Values[0] + ',' + #13#10 +
    '   "M": ' + ConfigPage.Values[1] + ',' + #13#10 +
    '   "Y": ' + ConfigPage.Values[2] + ',' + #13#10 +
    '   "K": ' + ConfigPage.Values[3] + ',' + #13#10 +
    '   "LC": ' + ConfigPage.Values[4] + ',' + #13#10 +
    '   "LM": ' + ConfigPage.Values[5] + ',' + #13#10 +
    '   "OP": ' + ConfigPage.Values[6] + #13#10 +
    '  }' + #13#10 +
    '}',
    False);

  Cmd := ExpandConstant('{app}\scripts\create_db.py');
  if not Exec(ExpandConstant('{cmd}'), '/c python "' + Cmd + '" --db-path "' + DbPath + '" --config "' + ConfigPath + '"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    Result := True;
  end
  else if ResultCode <> 0 then
  begin
    Result := True;
  end;
end;

procedure InitializeWizard;
begin
  ConfigWizardPage := CreateConfigPage;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  DbPath, BackupPath, Timestamp: String;
begin
  if CurStep = ssInstall then
  begin
    DbPath := ExpandConstant('{localappdata}\DPI Tintas HP\tintas_controle.db');
    if FileExists(DbPath) then
    begin
      Timestamp := GetDateTimeString('yyyymmdd_hhnnss', '-', '-');
      BackupPath := ExpandConstant('{localappdata}\DPI Tintas HP\tintas_controle_backup_' + Timestamp + '.db');
      FileCopy(DbPath, BackupPath, False);
    end;
  end;

  if CurStep = ssPostInstall then
  begin
    CreateDatabase(ConfigWizardPage);
  end;
end;
