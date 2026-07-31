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


def get_font_path(font_name: str) -> str:
    """Retorna caminho completo da fonte."""
    return get_asset_path(f"fonts/{font_name}.ttf")


class DPITheme:
    # --- PATHS DOS ASSETS ---
    IMAGES_DIR = get_asset_path("src/images")

    LOGO_PATH = get_asset_path("src/images/logo-64x64.png")
    FAVICON_PATH = get_asset_path("src/images/favicon.ico")

    DB_DIR = get_app_dir()
    DB_PATH = os.path.join(DB_DIR, "tintas_controle.db")

    # --- TOKENS DE CORES (Light, Dark) ---
    PRIMARY = ("#0F172A", "#0F172A")
    PRIMARY_LIGHT = ("#1E293B", "#1E293B")
    ACCENT = ("#0369A1", "#0369A1")
    ACCENT_HOVER = ("#0284C7", "#0284C7")

    BG_WINDOW = ("#F8FAFC", "#0F172A")
    SURFACE_CARD = ("#FFFFFF", "#1E293B")
    SURFACE_INPUT = ("#F1F5F9", "#0F172A")

    BORDER = ("#E2E8F0", "#334155")
    BORDER_LIGHT = ("#E2E8F0", "#334155")
    TEXT_MAIN = ("#0F172A", "#F8FAFC")
    TEXT_MUTED = ("#64748B", "#94A3B8")

    SUCCESS = ("#10B981", "#10B981")
    SUCCESS_BG = ("#D1FAE5", "#064E3B")
    DANGER = ("#EF4444", "#EF4444")
    WARNING = ("#F59E0B", "#F59E0B")

    # --- GLASSMORPHISM ---
    GLASS_BG = ("#FFFFFF", "#1E293B")
    GLASS_BORDER = ("#E2E8F0", "#334155")
    GLASS_SHADOW = ("#E2E8F0", "#000000")

    # --- PALETA CMYK PARA A INTERFACE ---
    CMYK = {
        "C": {"name": "Cyan", "hex": "#00AEEF", "text_color": "#FFFFFF"},
        "M": {"name": "Magenta", "hex": "#EC008C", "text_color": "#FFFFFF"},
        "Y": {"name": "Yellow", "hex": "#EAB308", "text_color": "#000000"},
        "K": {"name": "Black", "hex": "#334155", "text_color": "#FFFFFF"},
    }

    # --- TIPOGRAFIA (Poppins + Open Sans) ---
    FONT_FAMILY_HEADING = "Poppins"
    FONT_FAMILY_BODY = "Open Sans"
    FONT_FAMILY_MONO = "Consolas"

    FONT_TITLE = (FONT_FAMILY_HEADING, 16, "bold")
    FONT_SUBTITLE = (FONT_FAMILY_HEADING, 13, "bold")
    FONT_LABEL = (FONT_FAMILY_BODY, 11, "bold")
    FONT_VALUE = (FONT_FAMILY_MONO, 14, "bold")
    FONT_MENU = (FONT_FAMILY_BODY, 11)
    FONT_SMALL = (FONT_FAMILY_BODY, 10)
    FONT_BUTTON = (FONT_FAMILY_HEADING, 12, "bold")

    # --- RAIO DE BORDA ---
    RADIUS_CARD = 12
    RADIUS_INPUT = 8
    RADIUS_BUTTON = 10
    RADIUS_BADGE = 50

    # --- SOMBRAS ---
    SHADOW_SM = "#E2E8F0"
    SHADOW_MD = "#CBD5E1"
    SHADOW_LG = "#94A3B8"

    # --- TRANSICOES ---
    TRANSITION_FAST = 150
    TRANSITION_NORMAL = 200
    TRANSITION_SLOW = 300

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
