import subprocess
import sys
import os
import shutil


HIDDEN_IMPORTS = [
    "config",
    "config.theme",
    "controllers",
    "controllers.main_controller",
    "models",
    "models.database",
    "models.tinta_model",
    "views",
    "views.main_view",
    "views.config_modal",
    "views.components",
    "customtkinter",
    "PIL",
    "PIL._tkinter_finder",
    "sqlite3",
    "json",
    "tkinter",
    "tkinter.filedialog",
    "tkinter.messagebox",
]

SCRIPT_FILES = [
    "scripts/create_db.py",
]


def verify_scripts():
    """Verifica se os scripts necessários existem."""
    scripts_dir = os.path.join(os.path.dirname(__file__), "scripts")
    missing = []

    for script in SCRIPT_FILES:
        script_path = os.path.join(scripts_dir, os.path.basename(script))
        if not os.path.exists(script_path):
            missing.append(script)

    if missing:
        print(f"  AVISO: Scripts nao encontrados: {', '.join(missing)}")
        print("  O instalador nao criara o banco de dados automaticamente.")
        return False
    return True


def build():
    print("=" * 50)
    print("  DPI Tintas HP - Script de Build")
    print("=" * 50)
    print()

    print("[0/5] Verificando scripts auxiliares...")
    scripts_ok = verify_scripts()

    print()
    print("[1/5] Verificando PyInstaller...")
    try:
        import PyInstaller

        print(f"  PyInstaller {PyInstaller.__version__} encontrado")
    except ImportError:
        print("  PyInstaller nao encontrado. Instalando...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "pyinstaller"], check=True
        )

    print()
    print("[2/5] Gerando executavel...")

    sep = ";" if sys.platform == "win32" else ":"

    hidden_args = []
    for mod in HIDDEN_IMPORTS:
        hidden_args.extend(["--hidden-import", mod])

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconsole",
        "--onefile",
        "--name",
        "DPI-Tintas-HP",
        "--icon",
        f"src{os.sep}images{os.sep}app_icon.ico",
        "--add-data",
        f"src{os.sep}images{sep}src{os.sep}images",
        "--add-data",
        f"fonts{sep}fonts",
        *hidden_args,
        "--clean",
        "main.py",
    ]

    result = subprocess.run(cmd, capture_output=False)

    print()
    print("[3/5] Verificando resultado...")

    exe_path = os.path.join("dist", "DPI-Tintas-HP.exe")
    if not os.path.exists(exe_path):
        print()
        print("=" * 50)
        print("  ERRO: Executavel nao foi gerado!")
        print("  Verifique os erros acima.")
        print("=" * 50)
        sys.exit(1)

    size_mb = os.path.getsize(exe_path) / (1024 * 1024)
    print()
    print(f"  Executavel: {exe_path}")
    print(f"  Tamanho: {size_mb:.1f} MB")

    print()
    print("[4/5] Gerando instalador...")
    build_installer()


def build_installer():
    iscc_path = find_iscc()
    if not iscc_path:
        print("  Inno Setup nao encontrado. Pulando geracao do instalador.")
        print("  Para gerar o instalador, instale o Inno Setup:")
        print("  https://jrsoftware.org/isinfo.php")
        return

    result = subprocess.run(
        [iscc_path, "installer.iss"], capture_output=False
    )

    installer_path = os.path.join("installer", "DPI-Tintas-HP-Setup.exe")
    if os.path.exists(installer_path):
        size_mb = os.path.getsize(installer_path) / (1024 * 1024)
        print()
        print("=" * 50)
        print("  INSTALADOR GERADO COM SUCESSO!")
        print(f"  Instalador: {installer_path}")
        print(f"  Tamanho: {size_mb:.1f} MB")
        print("=" * 50)
    else:
        print()
        print("  AVISO: Instalador nao foi gerado.")
        print("  Verifique se o Inno Setup esta instalado corretamente.")


def find_iscc():
    common_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
        r"C:\Program Files\Inno Setup 5\ISCC.exe",
    ]
    for path in common_paths:
        if os.path.exists(path):
            return path

    shutil_which = shutil.which("iscc")
    if shutil_which:
        return shutil_which

    return None


if __name__ == "__main__":
    build()
