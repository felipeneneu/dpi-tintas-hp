import customtkinter as ctk
from config.theme import DPITheme


class ConfigModal(ctk.CTkToplevel):
    """Modal de configuracao de cartuchos - estilo macOS."""

    def __init__(self, master, config_atual: dict):
        super().__init__(master)

        self.title("Configurar Cartuchos")
        self.geometry("480x620")
        self.transient(master)
        self.grab_set()
        self.configure(fg_color=DPITheme.BG_WINDOW[0])

        self.resultado = None
        self.entries = {}

        self._criar_layout(config_atual)

    def _criar_layout(self, config: dict):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=DPITheme.SPACING_LG, pady=(DPITheme.SPACING_LG, DPITheme.SPACING_SM))

        ctk.CTkLabel(
            header,
            text="Configuracao dos Cartuchos",
            font=DPITheme.FONT_TITLE,
            text_color=DPITheme.TEXT_PRIMARY[0],
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Defina o preco (R$) de cada cartucho de 775ml",
            font=DPITheme.FONT_SMALL,
            text_color=DPITheme.TEXT_SECONDARY[0],
        ).pack(anchor="w", pady=(2, 0))

        scroll = ctk.CTkScrollableFrame(
            self, fg_color="transparent", height=380
        )
        scroll.pack(fill="both", expand=True, padx=DPITheme.SPACING_LG)

        for cor in DPITheme.CORES.keys():
            dados = config.get(cor, {"capacidade_ml": 775, "preco_centavos": 5000})
            self._criar_linha(scroll, cor, dados)

        botoes = ctk.CTkFrame(self, fg_color="transparent")
        botoes.pack(fill="x", padx=DPITheme.SPACING_LG, pady=(DPITheme.SPACING_SM, DPITheme.SPACING_LG))

        ctk.CTkButton(
            botoes,
            text="Cancelar",
            width=100,
            height=36,
            font=DPITheme.FONT_LABEL,
            fg_color="transparent",
            hover_color=DPITheme.BORDER_LIGHT[0],
            text_color=DPITheme.TEXT_SECONDARY[0],
            border_width=1,
            border_color=DPITheme.BORDER[0],
            corner_radius=DPITheme.RADIUS_SM,
            command=self._cancelar,
        ).pack(side="left")

        ctk.CTkButton(
            botoes,
            text="Salvar",
            width=100,
            height=36,
            font=DPITheme.FONT_LABEL,
            fg_color=DPITheme.ACCENT[0],
            hover_color=DPITheme.ACCENT_HOVER[0],
            corner_radius=DPITheme.RADIUS_SM,
            command=self._salvar,
        ).pack(side="right")

    def _criar_linha(self, parent, cor: str, dados: dict):
        info = DPITheme.CORES[cor]

        container = ctk.CTkFrame(
            parent,
            fg_color=DPITheme.SURFACE_CARD[0],
            corner_radius=DPITheme.RADIUS_SM,
            border_width=1,
            border_color=DPITheme.BORDER[0],
        )
        container.pack(fill="x", pady=4)

        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", padx=12, pady=(8, 4))

        badge = ctk.CTkFrame(
            header,
            width=28,
            height=28,
            fg_color=info["hex"],
            corner_radius=DPITheme.RADIUS_CIRCLE,
        )
        badge.pack(side="left", padx=(0, 8))
        badge.pack_propagate(False)

        ctk.CTkLabel(
            badge,
            text=cor,
            font=(DPITheme.FONT_FAMILY, 10, "bold"),
            text_color=info["text_color"],
        ).pack(expand=True)

        ctk.CTkLabel(
            header,
            text=info["name"],
            font=DPITheme.FONT_LABEL,
            text_color=DPITheme.TEXT_PRIMARY[0],
        ).pack(side="left")

        campos = ctk.CTkFrame(container, fg_color="transparent")
        campos.pack(fill="x", padx=12, pady=(0, 8))
        campos.columnconfigure(0, weight=1)
        campos.columnconfigure(1, weight=1)

        ctk.CTkLabel(
            campos,
            text="Preco (R$)",
            font=DPITheme.FONT_SMALL,
            text_color=DPITheme.TEXT_SECONDARY[0],
        ).grid(row=0, column=0, sticky="w")

        entry_preco = ctk.CTkEntry(
            campos,
            width=100,
            height=32,
            font=DPITheme.FONT_VALUE,
            justify="center",
            border_color=DPITheme.BORDER[0],
            fg_color=DPITheme.SURFACE_INPUT[0],
            corner_radius=DPITheme.RADIUS_SM,
        )
        entry_preco.grid(row=1, column=0, padx=(0, 8), sticky="w")
        preco_reais = dados["preco_centavos"] / 100
        entry_preco.insert(0, f"{preco_reais:.2f}".replace(".", ","))

        self.entries[cor] = {"preco": entry_preco}

    def _salvar(self):
        resultado = {}
        for cor, entries in self.entries.items():
            try:
                preco_texto = entries["preco"].get().replace(",", ".")
                preco = round(float(preco_texto) * 100)
            except (ValueError, TypeError):
                preco = 5000

            resultado[cor] = {
                "capacidade_ml": 775.0,
                "preco_centavos": max(1, preco),
            }

        self.resultado = resultado
        self.destroy()

    def _cancelar(self):
        self.resultado = None
        self.destroy()

    def obter_resultado(self) -> dict | None:
        self.wait_window()
        return self.resultado
