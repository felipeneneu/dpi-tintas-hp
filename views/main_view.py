import tkinter as tk
import customtkinter as ctk
from config.theme import DPITheme
from views.components import CmykCard, PrimaryButton, ResultCard


class MainView(ctk.CTk):
    """Janela principal do DPI Tintas HP."""

    def __init__(self):
        super().__init__()

        self.title("DPI Tintas HP - Controle de Consumo")
        self.geometry("820x740")
        self.minsize(720, 680)
        self.configure(fg_color=DPITheme.BG_WINDOW[0])

        try:
            from PIL import Image, ImageTk

            img = Image.open(DPITheme.LOGO_PATH)
            photo = ImageTk.PhotoImage(img)
            self.iconphoto(True, photo)
        except Exception:
            pass

        self._callback_calcular = None
        self._callback_configurar = None
        self._callback_exportar = None

        self._criar_menu_bar()
        self._criar_layout()

    def _criar_menu_bar(self):
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)

        menu_arquivo = tk.Menu(self.menu_bar, tearoff=0)
        menu_arquivo.add_command(
            label="Exportar JSON",
            command=lambda: self._on_exportar("json"),
        )
        menu_arquivo.add_command(
            label="Exportar SQL",
            command=lambda: self._on_exportar("sql"),
        )
        menu_arquivo.add_separator()
        menu_arquivo.add_command(label="Sair", command=self.destroy)
        self.menu_bar.add_cascade(label="Arquivo", menu=menu_arquivo)

        menu_editar = tk.Menu(self.menu_bar, tearoff=0)
        menu_editar.add_command(
            label="Configurar Cartuchos",
            command=self._on_configurar,
        )
        self.menu_bar.add_cascade(label="Editar", menu=menu_editar)

        menu_exibir = tk.Menu(self.menu_bar, tearoff=0)
        menu_exibir.add_command(
            label="Alternar Light/Dark",
            command=self._toggle_theme,
        )
        self.menu_bar.add_cascade(label="Exibir", menu=menu_exibir)

    def _toggle_theme(self):
        current = ctk.get_appearance_mode()
        new_mode = "Dark" if current == "Light" else "Light"
        ctk.set_appearance_mode(new_mode)

    def _criar_layout(self):
        self.main_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=DPITheme.BG_WINDOW[0],
        )
        self.main_frame.pack(fill="both", expand=True, padx=0, pady=0)

        self._criar_header()
        self._criar_cards_cmyk()
        self._criar_botao_calcular()
        self._criar_resultado()
        self._criar_footer()

    def _criar_header(self):
        header = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header.pack(fill="x", padx=32, pady=(24, 12))

        # Logo
        import os
        from PIL import Image

        logo_path = DPITheme.LOGO_PATH
        if os.path.exists(logo_path):
            try:
                img = Image.open(logo_path)
                logo = ctk.CTkImage(
                    light_image=img,
                    dark_image=img,
                    size=(48, 48),
                )
                ctk.CTkLabel(header, image=logo, text="").pack(
                    side="left", padx=(0, 16)
                )
            except Exception:
                pass

        # Textos
        textos = ctk.CTkFrame(header, fg_color="transparent")
        textos.pack(side="left")

        ctk.CTkLabel(
            textos,
            text="DPI Tintas HP",
            font=DPITheme.FONT_TITLE,
            text_color=DPITheme.TEXT_MAIN[0],
        ).pack(anchor="w")

        ctk.CTkLabel(
            textos,
            text="Controle de Consumo de Tintas - HP Latex 330",
            font=DPITheme.FONT_SMALL,
            text_color=DPITheme.TEXT_MUTED[0],
        ).pack(anchor="w")

        # Badge CMYK
        badge_frame = ctk.CTkFrame(header, fg_color="transparent")
        badge_frame.pack(side="right")

        for cor, info in DPITheme.CMYK.items():
            badge = ctk.CTkFrame(
                badge_frame,
                width=28,
                height=28,
                fg_color=info["hex"],
                corner_radius=DPITheme.RADIUS_BADGE,
            )
            badge.pack(side="left", padx=2)
            badge.pack_propagate(False)

            ctk.CTkLabel(
                badge,
                text=cor,
                font=(DPITheme.FONT_FAMILY_HEADING, 10, "bold"),
                text_color=info["text_color"],
            ).pack(expand=True)

    def _criar_cards_cmyk(self):
        # Titulo da secao
        secao = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        secao.pack(fill="x", padx=32, pady=(8, 4))

        ctk.CTkLabel(
            secao,
            text="Niveis de Tinta",
            font=DPITheme.FONT_SUBTITLE,
            text_color=DPITheme.TEXT_MAIN[0],
        ).pack(anchor="w")

        ctk.CTkLabel(
            secao,
            text="Informe o nivel atual e apos o uso de cada cartucho",
            font=DPITheme.FONT_SMALL,
            text_color=DPITheme.TEXT_MUTED[0],
        ).pack(anchor="w")

        # Cards
        self.cards_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.cards_frame.pack(fill="x", padx=32, pady=8)

        self.cards = {}
        for cor, info in DPITheme.CMYK.items():
            card = CmykCard(self.cards_frame, cor, info)
            card.pack(fill="x", pady=6)
            self.cards[cor] = card

    def _criar_botao_calcular(self):
        container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        container.pack(fill="x", padx=32, pady=16)

        self.btn_calcular = PrimaryButton(
            container,
            text="CALCULAR & REGISTRAR RODAGEM",
            command=self._on_calcular,
        )
        self.btn_calcular.pack(fill="x")

    def _criar_resultado(self):
        self.resultado = ResultCard(self.main_frame)
        self.resultado.pack(fill="x", padx=32, pady=(0, 16))

    def _criar_footer(self):
        footer = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        footer.pack(fill="x", padx=32, pady=(0, 24))

        ctk.CTkLabel(
            footer,
            text="DPI Visual - Solucoes em Impressao Digital",
            font=DPITheme.FONT_SMALL,
            text_color=DPITheme.TEXT_MUTED[0],
        ).pack(anchor="center")

    def _on_calcular(self):
        if self._callback_calcular:
            self._callback_calcular()

    def _on_configurar(self):
        if self._callback_configurar:
            self._callback_configurar()

    def _on_exportar(self, formato: str):
        if self._callback_exportar:
            self._callback_exportar(formato)

    def set_callbacks(self, calcular=None, configurar=None, exportar=None):
        self._callback_calcular = calcular
        self._callback_configurar = configurar
        self._callback_exportar = exportar

    def set_reabastecer_callbacks(self, callback):
        for card in self.cards.values():
            card.set_reabastecer_callback(callback)

    def get_niveis(self) -> dict:
        niveis = {}
        for cor, card in self.cards.items():
            niveis[cor] = card.get_niveis()
        return niveis

    def set_nivel_atual(self, cor: str, valor: float):
        if cor in self.cards:
            self.cards[cor].set_nivel_atual(valor)

    def set_niveis_finais(self, valores: dict):
        for cor, valor in valores.items():
            if cor in self.cards:
                self.cards[cor].set_nivel_final(valor)

    def set_resultado(self, custo_centavos: int, detalhes: str = ""):
        self.resultado.set_valor(custo_centavos)
        if detalhes:
            self.resultado.set_detalhes(detalhes)

    def mostrar_aviso(self, titulo: str, mensagem: str):
        dialog = ctk.CTkToplevel(self)
        dialog.title(titulo)
        dialog.geometry("400x200")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(fg_color=DPITheme.BG_WINDOW[0])

        ctk.CTkLabel(
            dialog,
            text=mensagem,
            font=DPITheme.FONT_LABEL,
            text_color=DPITheme.TEXT_MAIN[0],
            wraplength=350,
        ).pack(expand=True, padx=20)

        ctk.CTkButton(
            dialog,
            text="OK",
            command=dialog.destroy,
            fg_color=DPITheme.ACCENT[0],
            hover_color=DPITheme.ACCENT_HOVER[0],
            width=100,
        ).pack(pady=(0, 20))

    def mostrar_sucesso(self, mensagem: str):
        self.mostrar_aviso("Sucesso", mensagem)
