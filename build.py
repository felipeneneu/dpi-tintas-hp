import subprocess
import sys
import os


def build():
    print("=" * 50)
    print("  DPI Tintas HP - Script de Build")
    print("=" * 50)
    print()

    print("[1/3] Verificando PyInstaller...")
    try:
        import PyInstaller
        print(f"  PyInstaller {PyInstaller.__version__} encontrado")
    except ImportError:
        print("  PyInstaller nao encontrado. Instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)

    print()
    print("[2/3] Gerando executavel...")

    sep = ";" if sys.platform == "win32" else ":"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",
        "--onefile",
        "--name", "DPI-Tintas-HP",
        "--add-data", f"src{os.sep}images{sep}src{os.sep}images",
        "--add-data", f"fonts{sep}fonts",
        "--clean",
        "main.py",
    ]

    result = subprocess.run(cmd, capture_output=False)

    print()
    print("[3/3] Verificando resultado...")

    exe_path = os.path.join("dist", "DPI-Tintas-HP.exe")
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print()
        print("=" * 50)
        print(f"  BUILD CONCLUIDO COM SUCESSO!")
        print(f"  Executavel: {exe_path}")
        print(f"  Tamanho: {size_mb:.1f} MB")
        print("=" * 50)
    else:
        print()
        print("=" * 50)
        print("  ERRO: Executavel nao foi gerado!")
        print("  Verifique os erros acima.")
        print("=" * 50)
        sys.exit(1)


if __name__ == "__main__":
    build()
