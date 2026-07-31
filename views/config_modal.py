import customtkinter as ctk
from config.theme import DPITheme


class ConfigModal(ctk.CTkToplevel):
    """Modal de configuracao de cartuchos CMYK."""

    def __init__(self, master, config_atual: dict):
        super().__init__(master)

        self.title("Configurar Cartuchos")
        self.geometry("500x520")
        self.transient(master)
        self.grab_set()
        self.configure(fg_color=DPITheme.BG_WINDOW[0])

        self.resultado = None
        self.entries = {}

        self._criar_layout(config_atual)

    def _criar_layout(self, config: dict):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(20, 10))

        ctk.CTkLabel(
            header,
            text="Configura\u00e7\u00e3o dos Cartuchos",
            font=DPITheme.FONT_TITLE,
            text_color=DPITheme.TEXT_MAIN[0],
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Defina a capacidade (ml) e o pre\u00e7o (R$) de cada cartucho",
            font=DPITheme.FONT_SMALL,
            text_color=DPITheme.TEXT_MUTED[0],
        ).pack(anchor="w")

        scroll = ctk.CTkScrollableFrame(
            self, fg_color="transparent", height=320
        )
        scroll.pack(fill="both", expand=True, padx=25)

        for cor in ["C", "M", "Y", "K"]:
            dados = config.get(cor, {"capacidade_ml": 100, "preco_centavos": 5000})
            self._criar_linha(scroll, cor, dados)

        botoes = ctk.CTkFrame(self, fg_color="transparent")
        botoes.pack(fill="x", padx=25, pady=(10, 20))

        ctk.CTkButton(
            botoes,
            text="Cancelar",
            width=120,
            height=40,
            font=DPITheme.FONT_LABEL,
            fg_color=DPITheme.TEXT_MUTED[0],
            hover_color="#475569",
            corner_radius=DPITheme.RADIUS_BUTTON,
            command=self._cancelar,
        ).pack(side="left")

        ctk.CTkButton(
            botoes,
            text="Salvar",
            width=120,
            height=40,
            font=DPITheme.FONT_LABEL,
            fg_color=DPITheme.SUCCESS[0],
            hover_color="#059669",
            corner_radius=DPITheme.RADIUS_BUTTON,
            command=self._salvar,
        ).pack(side="right")

    def _criar_linha(self, parent, cor: str, dados: dict):
        info = DPITheme.CMYK[cor]

        container = ctk.CTkFrame(
            parent,
            fg_color=DPITheme.SURFACE_CARD[0],
            corner_radius=DPITheme.RADIUS_CARD,
            border_width=1,
            border_color=DPITheme.BORDER[0],
        )
        container.pack(fill="x", pady=5)

        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(10, 5))

        badge = ctk.CTkFrame(
            header,
            width=35,
            height=35,
            fg_color=info["hex"],
            corner_radius=6,
        )
        badge.pack(side="left", padx=(0, 10))
        badge.pack_propagate(False)

        ctk.CTkLabel(
            badge,
            text=cor,
            font=DPITheme.FONT_LABEL,
            text_color=info["text_color"],
        ).pack(expand=True)

        ctk.CTkLabel(
            header,
            text=info["name"],
            font=DPITheme.FONT_LABEL,
            text_color=DPITheme.TEXT_MAIN[0],
        ).pack(side="left")

        campos = ctk.CTkFrame(container, fg_color="transparent")
        campos.pack(fill="x", padx=15, pady=(0, 10))

        campos.columnconfigure(0, weight=1)
        campos.columnconfigure(1, weight=1)

        ctk.CTkLabel(
            campos,
            text="Capacidade (ml)",
            font=DPITheme.FONT_SMALL,
            text_color=DPITheme.TEXT_MUTED[0],
        ).grid(row=0, column=0, sticky="w")

        entry_cap = ctk.CTkEntry(
            campos,
            width=120,
            height=35,
            font=DPITheme.FONT_VALUE,
            justify="center",
            border_color=DPITheme.BORDER[0],
            fg_color=DPITheme.SURFACE_INPUT[0],
            corner_radius=DPITheme.RADIUS_INPUT,
        )
        entry_cap.grid(row=1, column=0, padx=(0, 10), sticky="w")
        entry_cap.insert(0, f"{dados['capacidade_ml']:.0f}")

        ctk.CTkLabel(
            campos,
            text="Pre\u00e7o (R$)",
            font=DPITheme.FONT_SMALL,
            text_color=DPITheme.TEXT_MUTED[0],
        ).grid(row=0, column=1, sticky="w")

        entry_preco = ctk.CTkEntry(
            campos,
            width=120,
            height=35,
            font=DPITheme.FONT_VALUE,
            justify="center",
            border_color=DPITheme.BORDER[0],
            fg_color=DPITheme.SURFACE_INPUT[0],
            corner_radius=DPITheme.RADIUS_INPUT,
        )
        entry_preco.grid(row=1, column=1, sticky="w")
        preco_reais = dados["preco_centavos"] / 100
        entry_preco.insert(0, f"{preco_reais:.2f}".replace(".", ","))

        self.entries[cor] = {"capacidade": entry_cap, "preco": entry_preco}

    def _salvar(self):
        resultado = {}
        for cor, entries in self.entries.items():
            try:
                cap = float(entries["capacidade"].get().replace(",", "."))
            except (ValueError, TypeError):
                cap = 100.0

            try:
                preco_texto = entries["preco"].get().replace(",", ".")
                preco = round(float(preco_texto) * 100)
            except (ValueError, TypeError):
                preco = 5000

            resultado[cor] = {
                "capacidade_ml": max(1.0, cap),
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
