import customtkinter as ctk
from config.theme import DPITheme


class RelatorioView(ctk.CTkFrame):
    """View de relatorios - estilo macOS."""

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=DPITheme.BG_WINDOW[0],
            **kwargs,
        )

        self._callback_gerar = None
        self._callback_exportar_pdf = None
        self._callback_exportar_excel = None

        self._criar_layout()

    def _criar_layout(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=DPITheme.SPACING_LG, pady=(DPITheme.SPACING_LG, DPITheme.SPACING_SM))

        ctk.CTkLabel(
            header,
            text="Relatorios",
            font=DPITheme.FONT_TITLE,
            text_color=DPITheme.TEXT_PRIMARY[0],
        ).pack(anchor="w")

        self._criar_seletor_data()
        self._criar_tipo_relatorio()
        self._criar_preview()
        self._criar_resumo()
        self._criar_botoes_exportar()

    def _criar_seletor_data(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="x", padx=DPITheme.SPACING_LG, pady=(0, DPITheme.SPACING_SM))
        container.columnconfigure(1, weight=1)
        container.columnconfigure(3, weight=1)

        ctk.CTkLabel(container, text="Periodo:", font=DPITheme.FONT_LABEL, text_color=DPITheme.TEXT_SECONDARY[0]).grid(row=0, column=0, padx=(0, 8), sticky="w")
        ctk.CTkLabel(container, text="De:", font=DPITheme.FONT_SMALL, text_color=DPITheme.TEXT_SECONDARY[0]).grid(row=0, column=1, padx=(0, 4), sticky="w")
        self.entry_data_inicio = ctk.CTkEntry(container, height=30, font=DPITheme.FONT_BODY, placeholder_text="DD/MM/AAAA", border_color=DPITheme.BORDER[0], fg_color=DPITheme.SURFACE_INPUT[0], corner_radius=DPITheme.RADIUS_SM)
        self.entry_data_inicio.grid(row=0, column=2, sticky="ew", padx=(0, 8))
        ctk.CTkLabel(container, text="Ate:", font=DPITheme.FONT_SMALL, text_color=DPITheme.TEXT_SECONDARY[0]).grid(row=0, column=3, padx=(0, 4), sticky="w")
        self.entry_data_fim = ctk.CTkEntry(container, height=30, font=DPITheme.FONT_BODY, placeholder_text="DD/MM/AAAA", border_color=DPITheme.BORDER[0], fg_color=DPITheme.SURFACE_INPUT[0], corner_radius=DPITheme.RADIUS_SM)
        self.entry_data_fim.grid(row=0, column=4, sticky="ew")

    def _criar_tipo_relatorio(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="x", padx=DPITheme.SPACING_LG, pady=(0, DPITheme.SPACING_SM))

        ctk.CTkLabel(container, text="Tipo:", font=DPITheme.FONT_LABEL, text_color=DPITheme.TEXT_SECONDARY[0]).pack(side="left", padx=(0, 8))

        self.combo_tipo = ctk.CTkComboBox(
            container,
            width=140,
            height=30,
            font=DPITheme.FONT_BODY,
            values=["Diario", "Semanal", "Personalizado"],
            border_color=DPITheme.BORDER[0],
            fg_color=DPITheme.SURFACE_INPUT[0],
            button_color=DPITheme.ACCENT[0],
            button_hover_color=DPITheme.ACCENT_HOVER[0],
            dropdown_fg_color=DPITheme.SURFACE_CARD[0],
            corner_radius=DPITheme.RADIUS_SM,
        )
        self.combo_tipo.pack(side="left")
        self.combo_tipo.set("Diario")

        ctk.CTkButton(
            container,
            text="Gerar",
            width=70,
            height=30,
            font=DPITheme.FONT_LABEL,
            fg_color=DPITheme.ACCENT[0],
            hover_color=DPITheme.ACCENT_HOVER[0],
            corner_radius=DPITheme.RADIUS_SM,
            command=self._on_gerar,
        ).pack(side="right")

    def _criar_preview(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=DPITheme.SPACING_LG, pady=(0, DPITheme.SPACING_SM))

        ctk.CTkLabel(
            container,
            text="Preview",
            font=DPITheme.FONT_LABEL,
            text_color=DPITheme.TEXT_PRIMARY[0],
        ).pack(anchor="w")

        self.preview_frame = ctk.CTkScrollableFrame(
            container,
            fg_color=DPITheme.SURFACE_CARD[0],
            corner_radius=DPITheme.RADIUS_MD,
            border_width=1,
            border_color=DPITheme.BORDER[0],
            height=160,
        )
        self.preview_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(
            self.preview_frame,
            text="Gere um relatorio para visualizar",
            font=DPITheme.FONT_LABEL,
            text_color=DPITheme.TEXT_SECONDARY[0],
        ).pack(pady=32)

    def _criar_resumo(self):
        container = ctk.CTkFrame(
            self,
            fg_color=DPITheme.SURFACE_CARD[0],
            corner_radius=DPITheme.RADIUS_MD,
            border_width=1,
            border_color=DPITheme.BORDER[0],
        )
        container.pack(fill="x", padx=DPITheme.SPACING_LG, pady=(0, DPITheme.SPACING_SM))

        ctk.CTkLabel(
            container,
            text="Resumo",
            font=DPITheme.FONT_LABEL,
            text_color=DPITheme.TEXT_PRIMARY[0],
        ).pack(anchor="w", padx=12, pady=(8, 4))

        stats = ctk.CTkFrame(container, fg_color="transparent")
        stats.pack(fill="x", padx=12, pady=(0, 8))
        stats.columnconfigure(0, weight=1)
        stats.columnconfigure(1, weight=1)
        stats.columnconfigure(2, weight=1)

        self.label_total_impressoes = self._criar_stat(stats, "Impressoes", "0", 0)
        self.label_custo_total = self._criar_stat(stats, "Custo Total", "R$ 0,00", 1)
        self.label_bobina_mais_usada = self._criar_stat(stats, "Bobina Top", "-", 2)

    def _criar_stat(self, parent, titulo: str, valor: str, col: int):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=col, padx=8, pady=4, sticky="ew")

        ctk.CTkLabel(
            frame,
            text=titulo,
            font=DPITheme.FONT_SMALL,
            text_color=DPITheme.TEXT_SECONDARY[0],
        ).pack(anchor="w")

        label = ctk.CTkLabel(
            frame,
            text=valor,
            font=(DPITheme.FONT_FAMILY, 15, "bold"),
            text_color=DPITheme.TEXT_PRIMARY[0],
        )
        label.pack(anchor="w")

        return label

    def _criar_botoes_exportar(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="x", padx=DPITheme.SPACING_LG, pady=(0, DPITheme.SPACING_LG))

        ctk.CTkButton(
            container,
            text="PDF",
            width=60,
            height=32,
            font=DPITheme.FONT_LABEL,
            fg_color=DPITheme.DANGER[0],
            hover_color=DPITheme.DANGER_HOVER[0],
            corner_radius=DPITheme.RADIUS_SM,
            command=self._on_exportar_pdf,
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            container,
            text="Excel",
            width=60,
            height=32,
            font=DPITheme.FONT_LABEL,
            fg_color=DPITheme.SUCCESS[0],
            hover_color=DPITheme.SUCCESS_HOVER[0],
            corner_radius=DPITheme.RADIUS_SM,
            command=self._on_exportar_excel,
        ).pack(side="left")

    def _on_gerar(self):
        if self._callback_gerar:
            self._callback_gerar(self._get_filtros())

    def _on_exportar_pdf(self):
        if self._callback_exportar_pdf:
            self._callback_exportar_pdf()

    def _on_exportar_excel(self):
        if self._callback_exportar_excel:
            self._callback_exportar_excel()

    def _get_filtros(self) -> dict:
        return {
            "data_inicio": self.entry_data_inicio.get().strip(),
            "data_fim": self.entry_data_fim.get().strip(),
            "tipo": self.combo_tipo.get(),
        }

    def set_callbacks(self, gerar=None, exportar_pdf=None, exportar_excel=None):
        self._callback_gerar = gerar
        self._callback_exportar_pdf = exportar_pdf
        self._callback_exportar_excel = exportar_excel

    def set_preview(self, texto: str):
        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self.preview_frame,
            text=texto,
            font=DPITheme.FONT_SMALL,
            text_color=DPITheme.TEXT_PRIMARY[0],
            justify="left",
            wraplength=520,
        ).pack(anchor="w", padx=10, pady=10)

    def set_resumo(
        self,
        total_impressoes: int = 0,
        custo_total_centavos: int = 0,
        bobina_mais_usada: str = "-",
    ):
        self.label_total_impressoes.configure(text=str(total_impressoes))
        self.label_custo_total.configure(
            text=DPITheme.formatar_reais(custo_total_centavos)
        )
        self.label_bobina_mais_usada.configure(text=bobina_mais_usada)
