import customtkinter as ctk
from config.theme import DPITheme


class PercentEntry(ctk.CTkFrame):
    """Campo de entrada de percentual com entrada limitada a 0-100."""

    def __init__(self, master, placeholder="0%", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.var = ctk.StringVar(value="")

        self.entry = ctk.CTkEntry(
            self,
            width=90,
            height=42,
            font=DPITheme.FONT_VALUE,
            justify="center",
            textvariable=self.var,
            placeholder_text=placeholder,
            border_color=DPITheme.BORDER[0],
            fg_color=DPITheme.SURFACE_INPUT[0],
            corner_radius=DPITheme.RADIUS_INPUT,
            border_width=1,
        )
        self.entry.pack(side="right")

        self.suffix = ctk.CTkLabel(
            self,
            text="%",
            font=DPITheme.FONT_LABEL,
            text_color=DPITheme.TEXT_MUTED[0],
            width=15,
        )
        self.suffix.pack(side="left", padx=(0, 2))

        self.entry.bind("<FocusOut>", self._validar)
        self.entry.bind("<Return>", self._validar)
        self.entry.bind("<KeyRelease>", self._filtrar_teclas)
        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)

    def _on_focus_in(self, event):
        self.entry.configure(border_color=DPITheme.ACCENT[0], border_width=2)

    def _on_focus_out(self, event):
        self.entry.configure(border_color=DPITheme.BORDER[0], border_width=1)
        self._validar()

    def _filtrar_teclas(self, event):
        texto = self.var.get()
        novo = "".join(c for c in texto if c.isdigit() or c == ".")
        if novo != texto:
            self.var.set(novo)

    def _validar(self, event=None):
        try:
            val = float(self.var.get())
            val = max(0.0, min(100.0, val))
            self.var.set(f"{val:.1f}")
        except (ValueError, TypeError):
            if self.var.get().strip():
                self.var.set("0.0")

    def get(self) -> float:
        try:
            return float(self.var.get())
        except (ValueError, TypeError):
            return 0.0

    def set(self, valor: float):
        self.var.set(f"{valor:.1f}")


class CmykCard(ctk.CTkFrame):
    """Card de uma cor CMYK com campos inicial/final e botao reabastecer."""

    def __init__(self, master, cor: str, cor_info: dict, **kwargs):
        super().__init__(
            master,
            fg_color=DPITheme.SURFACE_CARD[0],
            corner_radius=DPITheme.RADIUS_CARD,
            border_width=1,
            border_color=DPITheme.BORDER[0],
            height=80,
            **kwargs,
        )

        self.cor = cor
        self.cor_info = cor_info

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=0)
        self.columnconfigure(3, weight=1)
        self.columnconfigure(4, weight=0)

        self._criar_badge()
        self._criar_entrada_ini()
        self._criar_seta()
        self._criar_entrada_fim()
        self._criar_botao_reabastecer()

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, event):
        self.configure(border_color=DPITheme.ACCENT[0], border_width=2)

    def _on_leave(self, event):
        self.configure(border_color=DPITheme.BORDER[0], border_width=1)

    def _criar_badge(self):
        badge = ctk.CTkFrame(
            self,
            width=48,
            height=48,
            fg_color=self.cor_info["hex"],
            corner_radius=DPITheme.RADIUS_BADGE,
        )
        badge.grid(row=0, column=0, padx=16, pady=16)
        badge.grid_propagate(False)

        ctk.CTkLabel(
            badge,
            text=self.cor,
            font=DPITheme.FONT_TITLE,
            text_color=self.cor_info["text_color"],
        ).pack(expand=True)

        ctk.CTkLabel(
            self,
            text=self.cor_info["name"],
            font=DPITheme.FONT_LABEL,
            text_color=DPITheme.TEXT_MUTED[0],
        ).grid(row=1, column=0, padx=16, pady=(0, 16), sticky="w")

    def _criar_entrada_ini(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=0, column=1, padx=8, pady=16, sticky="nsew")

        ctk.CTkLabel(
            container,
            text="Atual",
            font=DPITheme.FONT_SMALL,
            text_color=DPITheme.TEXT_MUTED[0],
        ).pack(anchor="w")

        self.entry_ini = PercentEntry(container)
        self.entry_ini.pack(anchor="w")

    def _criar_seta(self):
        ctk.CTkLabel(
            self,
            text="\u279C",
            font=(DPITheme.FONT_FAMILY_HEADING, 18),
            text_color=DPITheme.ACCENT[0],
        ).grid(row=0, column=2, padx=12, pady=16)

    def _criar_entrada_fim(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=0, column=3, padx=8, pady=16, sticky="nsew")

        ctk.CTkLabel(
            container,
            text="Apos uso",
            font=DPITheme.FONT_SMALL,
            text_color=DPITheme.TEXT_MUTED[0],
        ).pack(anchor="w")

        self.entry_fim = PercentEntry(container)
        self.entry_fim.pack(anchor="w")

    def _criar_botao_reabastecer(self):
        self.btn_reabastecer = ctk.CTkButton(
            self,
            text="100%",
            width=65,
            height=42,
            font=DPITheme.FONT_BUTTON,
            fg_color=DPITheme.DANGER[0],
            hover_color="#DC2626",
            corner_radius=DPITheme.RADIUS_BUTTON,
            command=self._on_reabastecer,
        )
        self.btn_reabastecer.grid(row=0, column=4, padx=16, pady=16)

        self._callback_reabastecer = None

    def _on_reabastecer(self):
        if self._callback_reabastecer:
            self._callback_reabastecer(self.cor)

    def set_reabastecer_callback(self, callback):
        self._callback_reabastecer = callback

    def get_niveis(self) -> tuple[float, float]:
        return self.entry_ini.get(), self.entry_fim.get()

    def set_nivel_atual(self, valor: float):
        self.entry_ini.set(valor)

    def set_nivel_final(self, valor: float):
        self.entry_fim.set(valor)


class PrimaryButton(ctk.CTkButton):
    """Botao principal estilizado DPI."""

    def __init__(self, master, text: str, command=None, **kwargs):
        super().__init__(
            master,
            text=text,
            command=command,
            height=52,
            font=DPITheme.FONT_BUTTON,
            fg_color=DPITheme.ACCENT[0],
            hover_color=DPITheme.ACCENT_HOVER[0],
            corner_radius=DPITheme.RADIUS_BUTTON,
            **kwargs,
        )


class ResultCard(ctk.CTkFrame):
    """Card de resultado com custo total."""

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=DPITheme.SUCCESS[0],
            corner_radius=DPITheme.RADIUS_CARD,
            border_width=0,
            **kwargs,
        )

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)

        ctk.CTkLabel(
            self,
            text="Custo Total da Rodagem",
            font=DPITheme.FONT_LABEL,
            text_color="#FFFFFF",
        ).grid(row=0, column=0, padx=24, pady=(16, 0), sticky="w")

        self.label_valor = ctk.CTkLabel(
            self,
            text="R$ 0,00",
            font=(DPITheme.FONT_FAMILY_HEADING, 28, "bold"),
            text_color="#FFFFFF",
        )
        self.label_valor.grid(row=1, column=0, padx=24, pady=(0, 16), sticky="w")

        self.label_detalhes = ctk.CTkLabel(
            self,
            text="",
            font=DPITheme.FONT_SMALL,
            text_color="#FFFFFF",
        )
        self.label_detalhes.grid(
            row=1, column=1, padx=24, pady=(0, 16), sticky="e"
        )

    def set_valor(self, custo_centavos: int):
        self.label_valor.configure(text=DPITheme.formatar_reais(custo_centavos))

    def set_detalhes(self, texto: str):
        self.label_detalhes.configure(text=texto)
