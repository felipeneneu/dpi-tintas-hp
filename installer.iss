[Setup]
AppName=DPI Tintas HP
AppVersion=1.0.0
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
  PrecoCyanEdit: TNewEdit;
  PrecoMagentaEdit: TNewEdit;
  PrecoYellowEdit: TNewEdit;
  PrecoBlackEdit: TNewEdit;
  CapacidadeEdit: TNewEdit;
  NivelEdit: TNewEdit;

function CreateConfigPage: TInputQueryWizardPage;
begin
  Result := CreateInputQueryPage(wpSelectDir,
    'Configuracao Inicial',
    'Configure os precos e capacidades dos cartuchos.',
    'Estas configuracoes serao aplicadas ao banco de dados. Voce pode altera-las depois pelo programa.');

  Result.Add('Preco do Cartucho Cyan (R$):', False);
  Result.Values[0] := '50.00';

  Result.Add('Preco do Cartucho Magenta (R$):', False);
  Result.Values[1] := '50.00';

  Result.Add('Preco do Cartucho Yellow (R$):', False);
  Result.Values[2] := '50.00';

  Result.Add('Preco do Cartucho Black (R$):', False);
  Result.Values[3] := '50.00';

  Result.Add('Capacidade dos Cartuchos (ml):', False);
  Result.Values[4] := '100';

  Result.Add('Nivel Inicial (%):', False);
  Result.Values[5] := '100';
end;

procedure BackupExistingDatabase;
var
  DbPath, BackupPath, Timestamp: String;
begin
  DbPath := ExpandConstant('{app}\tintas_controle.db');
  if FileExists(DbPath) then
  begin
    Timestamp := GetDateTimeString('yyyymmdd_hhnnss', '-', '-');
    BackupPath := ExpandConstant('{app}\tintas_controle_backup_' + Timestamp + '.db');
    FileCopy(DbPath, BackupPath, False);
  end;
end;

function CreateDatabase(ConfigPage: TInputQueryWizardPage): Boolean;
var
  DbPath, Cmd, ConfigPath: String;
  ResultCode: Integer;
  PrecoCyan, PrecoMagenta, PrecoYellow, PrecoBlack: String;
  Capacidade, Nivel: String;
begin
  Result := True;
  DbPath := ExpandConstant('{localappdata}\DPI Tintas HP\tintas_controle.db');

  PrecoCyan := ConfigPage.Values[0];
  PrecoMagenta := ConfigPage.Values[1];
  PrecoYellow := ConfigPage.Values[2];
  PrecoBlack := ConfigPage.Values[3];
  Capacidade := ConfigPage.Values[4];
  Nivel := ConfigPage.Values[5];

  ConfigPath := ExpandConstant('{tmp}\installer_config.json');
  SaveStringToFile(ConfigPath,
    '{"capacidade_ml": ' + Capacidade + ',' + #13#10 +
    ' "nivel_atual_pct": ' + Nivel + ',' + #13#10 +
    ' "precos": {' + #13#10 +
    '   "C": ' + PrecoCyan + ',' + #13#10 +
    '   "M": ' + PrecoMagenta + ',' + #13#10 +
    '   "Y": ' + PrecoYellow + ',' + #13#10 +
    '   "K": ' + PrecoBlack + #13#10 +
    '  }' + #13#10 +
    '}',
    False);

  Cmd := ExpandConstant('{app}\scripts\create_db.py');
  if not Exec(ExpandConstant('{cmd}'), '/c python "' + Cmd + '" --db-path "' + DbPath + '" --config "' + ConfigPath + '"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    MsgBox('Erro ao executar criacao do banco de dados.', mbInformation, MB_OK);
    Result := True;
  end
  else if ResultCode <> 0 then
  begin
    MsgBox('Erro ao criar o banco de dados. O programa criara na primeira execucao.', mbInformation, MB_OK);
    Result := True;
  end;
end;

var
  ConfigWizardPage: TInputQueryWizardPage;

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
