import customtkinter as ctk
from config.theme import DPITheme


class HistoricoView(ctk.CTkFrame):
    """View de historico e busca - estilo macOS."""

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=DPITheme.BG_WINDOW[0],
            **kwargs,
        )

        self._callback_buscar = None
        self._resultados = []

        self._criar_layout()

    def _criar_layout(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=DPITheme.SPACING_LG, pady=(DPITheme.SPACING_LG, DPITheme.SPACING_SM))

        ctk.CTkLabel(
            header,
            text="Historico de Rodagens",
            font=DPITheme.FONT_TITLE,
            text_color=DPITheme.TEXT_PRIMARY[0],
        ).pack(anchor="w")

        self._criar_barra_busca()
        self._criar_filtros()
        self._criar_tabela()
        self._criar_detalhes()

    def _criar_barra_busca(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="x", padx=DPITheme.SPACING_LG, pady=(0, DPITheme.SPACING_SM))

        self.entry_busca = ctk.CTkEntry(
            container,
            height=36,
            font=DPITheme.FONT_BODY,
            placeholder_text="Buscar por pedido, bobina, arquivo...",
            border_color=DPITheme.BORDER[0],
            fg_color=DPITheme.SURFACE_INPUT[0],
            corner_radius=DPITheme.RADIUS_SM,
        )
        self.entry_busca.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            container,
            text="Buscar",
            width=80,
            height=36,
            font=DPITheme.FONT_LABEL,
            fg_color=DPITheme.ACCENT[0],
            hover_color=DPITheme.ACCENT_HOVER[0],
            corner_radius=DPITheme.RADIUS_SM,
            command=self._on_buscar,
        ).pack(side="right")

    def _criar_filtros(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="x", padx=DPITheme.SPACING_LG, pady=(0, DPITheme.SPACING_SM))
        container.columnconfigure(1, weight=1)
        container.columnconfigure(3, weight=1)

        ctk.CTkLabel(container, text="De:", font=DPITheme.FONT_SMALL, text_color=DPITheme.TEXT_SECONDARY[0]).grid(row=0, column=0, padx=(0, 4), sticky="w")
        self.entry_data_inicio = ctk.CTkEntry(container, height=30, font=DPITheme.FONT_BODY, placeholder_text="DD/MM/AAAA", border_color=DPITheme.BORDER[0], fg_color=DPITheme.SURFACE_INPUT[0], corner_radius=DPITheme.RADIUS_SM)
        self.entry_data_inicio.grid(row=0, column=1, sticky="ew", padx=(0, 8))

        ctk.CTkLabel(container, text="Ate:", font=DPITheme.FONT_SMALL, text_color=DPITheme.TEXT_SECONDARY[0]).grid(row=0, column=2, padx=(0, 4), sticky="w")
        self.entry_data_fim = ctk.CTkEntry(container, height=30, font=DPITheme.FONT_BODY, placeholder_text="DD/MM/AAAA", border_color=DPITheme.BORDER[0], fg_color=DPITheme.SURFACE_INPUT[0], corner_radius=DPITheme.RADIUS_SM)
        self.entry_data_fim.grid(row=0, column=3, sticky="ew", padx=(0, 8))

        ctk.CTkLabel(container, text="Pedido:", font=DPITheme.FONT_SMALL, text_color=DPITheme.TEXT_SECONDARY[0]).grid(row=0, column=4, padx=(0, 4), sticky="w")
        self.combo_pedido = ctk.CTkComboBox(container, height=30, font=DPITheme.FONT_BODY, values=["Todos"], border_color=DPITheme.BORDER[0], fg_color=DPITheme.SURFACE_INPUT[0], button_color=DPITheme.ACCENT[0], button_hover_color=DPITheme.ACCENT_HOVER[0], dropdown_fg_color=DPITheme.SURFACE_CARD[0], corner_radius=DPITheme.RADIUS_SM)
        self.combo_pedido.grid(row=0, column=5)

    def _criar_tabela(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=DPITheme.SPACING_LG, pady=(0, DPITheme.SPACING_SM))

        self.tabela_frame = ctk.CTkScrollableFrame(
            container,
            fg_color=DPITheme.SURFACE_CARD[0],
            corner_radius=DPITheme.RADIUS_MD,
            border_width=1,
            border_color=DPITheme.BORDER[0],
        )
        self.tabela_frame.pack(fill="both", expand=True)

        header = ctk.CTkFrame(self.tabela_frame, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(8, 4))

        for texto in ["Data", "Pedido", "Arquivo", "Custo", "Duracao"]:
            ctk.CTkLabel(
                header,
                text=texto,
                font=DPITheme.FONT_SMALL,
                text_color=DPITheme.TEXT_SECONDARY[0],
                width=100,
            ).pack(side="left", padx=4)

        ctk.CTkLabel(
            self.tabela_frame,
            text="Nenhum resultado encontrado",
            font=DPITheme.FONT_LABEL,
            text_color=DPITheme.TEXT_SECONDARY[0],
        ).pack(pady=40)

    def _criar_detalhes(self):
        container = ctk.CTkFrame(
            self,
            fg_color=DPITheme.SURFACE_CARD[0],
            corner_radius=DPITheme.RADIUS_MD,
            border_width=1,
            border_color=DPITheme.BORDER[0],
        )
        container.pack(fill="x", padx=DPITheme.SPACING_LG, pady=(0, DPITheme.SPACING_LG))

        ctk.CTkLabel(
            container,
            text="Detalhes da Rodagem",
            font=DPITheme.FONT_LABEL,
            text_color=DPITheme.TEXT_PRIMARY[0],
        ).pack(anchor="w", padx=12, pady=(8, 4))

        self.label_detalhes = ctk.CTkLabel(
            container,
            text="Selecione um registro para ver detalhes",
            font=DPITheme.FONT_SMALL,
            text_color=DPITheme.TEXT_SECONDARY[0],
            wraplength=520,
        )
        self.label_detalhes.pack(anchor="w", padx=12, pady=(0, 8))

    def _on_buscar(self):
        if self._callback_buscar:
            self._callback_buscar(self._get_filtros())

    def _get_filtros(self) -> dict:
        return {
            "busca": self.entry_busca.get().strip(),
            "data_inicio": self.entry_data_inicio.get().strip(),
            "data_fim": self.entry_data_fim.get().strip(),
            "pedido": self.combo_pedido.get(),
        }

    def set_buscar_callback(self, callback):
        self._callback_buscar = callback

    def set_resultados(self, resultados: list[dict]):
        self._resultados = resultados
        self._atualizar_tabela()

    def _atualizar_tabela(self):
        for widget in self.tabela_frame.winfo_children():
            widget.destroy()

        if not self._resultados:
            ctk.CTkLabel(
                self.tabela_frame,
                text="Nenhum resultado encontrado",
                font=DPITheme.FONT_LABEL,
                text_color=DPITheme.TEXT_SECONDARY[0],
            ).pack(pady=40)
            return

        header = ctk.CTkFrame(self.tabela_frame, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(8, 4))

        for texto in ["Data", "Pedido", "Arquivo", "Custo", "Duracao"]:
            ctk.CTkLabel(
                header,
                text=texto,
                font=DPITheme.FONT_SMALL,
                text_color=DPITheme.TEXT_SECONDARY[0],
                width=100,
            ).pack(side="left", padx=4)

        for idx, reg in enumerate(self._resultados):
            linha = ctk.CTkFrame(
                self.tabela_frame,
                fg_color="transparent",
                height=30,
            )
            linha.pack(fill="x", padx=10, pady=1)

            for campo in ["data", "pedido", "arquivo", "custo", "duracao"]:
                ctk.CTkLabel(
                    linha,
                    text=str(reg.get(campo, "")),
                    font=DPITheme.FONT_SMALL,
                    text_color=DPITheme.TEXT_PRIMARY[0],
                    width=100,
                ).pack(side="left", padx=4)

    def set_detalhes(self, texto: str):
        self.label_detalhes.configure(text=texto)

    def set_pedidos(self, pedidos: list[str]):
        valores = ["Todos"] + pedidos if pedidos else ["Todos"]
        self.combo_pedido.configure(values=valores)
        self.combo_pedido.set("Todos")
