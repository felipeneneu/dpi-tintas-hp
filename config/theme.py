import os
import sys


def get_asset_path(relative_path: str) -> str:
    """Resolve path para dev e PyInstaller (_MEIPASS)."""
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def get_app_dir() -> str:
    """Retorna diretorio do executavel ou script."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_data_dir() -> str:
    """Retorna diretorio gravavel para dados (banco de configuracoes)."""
    if getattr(sys, "frozen", False):
        data_dir = os.path.join(os.environ.get("LOCALAPPDATA", ""), "DPI Tintas HP")
    else:
        data_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


def get_font_path(font_name: str) -> str:
    """Retorna caminho completo da fonte."""
    return get_asset_path(f"fonts/{font_name}.ttf")


class DPITheme:
    IMAGES_DIR = get_asset_path("src/images")
    LOGO_PATH = get_asset_path("src/images/logo-64x64.png")
    FAVICON_PATH = get_asset_path("src/images/favicon.ico")

    DB_DIR = get_data_dir()
    DB_PATH = os.path.join(DB_DIR, "tintas_controle.db")

    # --- CORES macOS ---
    BG_WINDOW = ("#F5F5F7", "#1C1C1E")
    SURFACE_CARD = ("#FFFFFF", "#2C2C2E")
    SURFACE_INPUT = ("#E5E5EA", "#3A3A3C")

    ACCENT = ("#007AFF", "#0A84FF")
    ACCENT_HOVER = ("#0066CC", "#007AFF")
    ACCENT_LIGHT = ("#B3D7FF", "#0A84FF")

    SUCCESS = ("#34C759", "#30D158")
    SUCCESS_HOVER = ("#2DA44E", "#28BD4B")
    DANGER = ("#FF3B30", "#FF453A")
    DANGER_HOVER = ("#D32F2F", "#D32F2F")
    WARNING = ("#FF9500", "#FF9F0A")
    WARNING_HOVER = ("#E08600", "#E08600")

    TEXT_PRIMARY = ("#1D1D1F", "#F5F5F7")
    TEXT_SECONDARY = ("#6E6E73", "#98989D")
    TEXT_TERTIARY = ("#AEAEB2", "#636366")
    TEXT_ON_ACCENT = ("#FFFFFF", "#FFFFFF")

    BORDER = ("#D2D2D7", "#48484A")
    BORDER_LIGHT = ("#E5E5EA", "#3A3A3C")
    DIVIDER = ("#C6C6C8", "#48484A")

    # --- PALETA DE CORES PARA A INTERFACE (7 cores) ---
    CORES = {
        "C": {"name": "Cyan", "hex": "#00AEEF", "text_color": "#FFFFFF"},
        "M": {"name": "Magenta", "hex": "#EC008C", "text_color": "#FFFFFF"},
        "Y": {"name": "Yellow", "hex": "#EAB308", "text_color": "#000000"},
        "K": {"name": "Black", "hex": "#334155", "text_color": "#FFFFFF"},
        "LC": {"name": "Light Cyan", "hex": "#67D5FF", "text_color": "#000000"},
        "LM": {"name": "Light Magenta", "hex": "#F57FC7", "text_color": "#000000"},
        "OP": {"name": "Opaca", "hex": "#D1D5DB", "text_color": "#000000"},
    }
    CMYK = CORES

    # --- TIPOGRAFIA ---
    FONT_FAMILY = "Segoe UI"
    FONT_MONO = "Cascadia Code"

    FONT_TITLE = (FONT_FAMILY, 18, "bold")
    FONT_SUBTITLE = (FONT_FAMILY, 14, "bold")
    FONT_LABEL = (FONT_FAMILY, 12, "bold")
    FONT_BODY = (FONT_FAMILY, 12)
    FONT_SMALL = (FONT_FAMILY, 11)
    FONT_BUTTON = (FONT_FAMILY, 12, "bold")
    FONT_VALUE = (FONT_MONO, 13, "bold")
    FONT_MENU = (FONT_FAMILY, 12)

    # --- ESPACAMENTO (Grid 8px) ---
    SPACING_XS = 4
    SPACING_SM = 8
    SPACING_MD = 16
    SPACING_LG = 24
    SPACING_XL = 32

    # --- RAIO DE BORDA ---
    RADIUS_SM = 6
    RADIUS_MD = 10
    RADIUS_LG = 14
    RADIUS_XL = 20
    RADIUS_CIRCLE = 9999

    # --- LEGADO (manter compatibilidade) ---
    RADIUS_CARD = RADIUS_MD
    RADIUS_INPUT = RADIUS_SM
    RADIUS_BUTTON = RADIUS_SM
    RADIUS_BADGE = RADIUS_CIRCLE

    # --- MASCARA MONETARIA (centavos) ---
    @staticmethod
    def formatar_reais(valor_centavos: int) -> str:
        """Formata valor em centavos para R$ XX,XX"""
        reais = valor_centavos // 100
        centavos = valor_centavos % 100
        return f"R$ {reais},{centavos:02d}"

    @staticmethod
    def parse_reais(texto: str) -> int:
        """Extrai centavos de texto R$ XX,XX ou XX,XX"""
        import re

        numeros = re.sub(r"[^\d,]", "", texto)
        numeros = numeros.replace(",", ".")
        try:
            return round(float(numeros) * 100)
        except (ValueError, TypeError):
            return 0
