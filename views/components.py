import customtkinter as ctk
from config.theme import DPITheme


class MlEntry(ctk.CTkFrame):
    """Campo de entrada de mililitros estilo macOS."""

    def __init__(self, master, placeholder="0", max_ml=775, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.max_ml = max_ml
        self.var = ctk.StringVar(value="")

        self.entry = ctk.CTkEntry(
            self,
            width=80,
            height=36,
            font=DPITheme.FONT_VALUE,
            justify="right",
            textvariable=self.var,
            placeholder_text=placeholder,
            border_color=DPITheme.BORDER[0],
            fg_color=DPITheme.SURFACE_INPUT[0],
            corner_radius=DPITheme.RADIUS_SM,
            border_width=1,
        )
        self.entry.pack(side="left")

        self.suffix = ctk.CTkLabel(
            self,
            text=" ml",
            font=DPITheme.FONT_SMALL,
            text_color=DPITheme.TEXT_SECONDARY[0],
            width=24,
        )
        self.suffix.pack(side="left")

        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)
        self.entry.bind("<Return>", self._validar)
        self.entry.bind("<KeyRelease>", self._filtrar_teclas)

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
            val = max(0.0, min(self.max_ml, val))
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


class ColorCard(ctk.CTkFrame):
    """Card de cor estilo macOS com campos inicial/final."""

    def __init__(self, master, cor: str, cor_info: dict, **kwargs):
        super().__init__(
            master,
            fg_color=DPITheme.SURFACE_CARD[0],
            corner_radius=DPITheme.RADIUS_MD,
            border_width=1,
            border_color=DPITheme.BORDER[0],
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
        self.configure(border_color=DPITheme.ACCENT[0], border_width=1.5)

    def _on_leave(self, event):
        self.configure(border_color=DPITheme.BORDER[0], border_width=1)

    def _criar_badge(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=0, column=0, rowspan=2, padx=12, pady=12)

        badge = ctk.CTkFrame(
            container,
            width=40,
            height=40,
            fg_color=self.cor_info["hex"],
            corner_radius=DPITheme.RADIUS_CIRCLE,
        )
        badge.pack()
        badge.pack_propagate(False)

        ctk.CTkLabel(
            badge,
            text=self.cor,
            font=(DPITheme.FONT_FAMILY, 11, "bold"),
            text_color=self.cor_info["text_color"],
        ).pack(expand=True)

        ctk.CTkLabel(
            container,
            text=self.cor_info["name"],
            font=DPITheme.FONT_SMALL,
            text_color=DPITheme.TEXT_SECONDARY[0],
        ).pack(pady=(4, 0))

    def _criar_entrada_ini(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=0, column=1, padx=4, pady=(10, 2), sticky="ew")

        ctk.CTkLabel(
            container,
            text="Inicial",
            font=DPITheme.FONT_SMALL,
            text_color=DPITheme.TEXT_SECONDARY[0],
        ).pack(anchor="w")

        self.entry_ini = MlEntry(container)
        self.entry_ini.pack(anchor="w", pady=(2, 0))

    def _criar_seta(self):
        ctk.CTkLabel(
            self,
            text="\u2192",
            font=(DPITheme.FONT_FAMILY, 16),
            text_color=DPITheme.TEXT_TERTIARY[0],
        ).grid(row=0, column=2, padx=4, pady=(10, 0))

    def _criar_entrada_fim(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=0, column=3, padx=4, pady=(10, 2), sticky="ew")

        ctk.CTkLabel(
            container,
            text="Final",
            font=DPITheme.FONT_SMALL,
            text_color=DPITheme.TEXT_SECONDARY[0],
        ).pack(anchor="w")

        self.entry_fim = MlEntry(container)
        self.entry_fim.pack(anchor="w", pady=(2, 0))

    def _criar_botao_reabastecer(self):
        self.btn_reabastecer = ctk.CTkButton(
            self,
            text="775",
            width=56,
            height=32,
            font=DPITheme.FONT_SMALL,
            fg_color=DPITheme.DANGER[0],
            hover_color=DPITheme.DANGER_HOVER[0],
            corner_radius=DPITheme.RADIUS_SM,
            command=self._on_reabastecer,
        )
        self.btn_reabastecer.grid(row=0, column=4, padx=12, pady=(10, 0))

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
    """Botao primario estilo macOS."""

    def __init__(self, master, text: str, command=None, **kwargs):
        super().__init__(
            master,
            text=text,
            command=command,
            height=44,
            font=DPITheme.FONT_BUTTON,
            fg_color=DPITheme.ACCENT[0],
            hover_color=DPITheme.ACCENT_HOVER[0],
            corner_radius=DPITheme.RADIUS_SM,
            **kwargs,
        )


class SecondaryButton(ctk.CTkButton):
    """Botao secundario estilo macOS (borda + fundo transparente)."""

    def __init__(self, master, text: str, command=None, **kwargs):
        super().__init__(
            master,
            text=text,
            command=command,
            height=36,
            font=DPITheme.FONT_BUTTON,
            fg_color="transparent",
            hover_color=DPITheme.BORDER_LIGHT[0],
            text_color=DPITheme.TEXT_PRIMARY[0],
            border_width=1,
            border_color=DPITheme.BORDER[0],
            corner_radius=DPITheme.RADIUS_SM,
            **kwargs,
        )


class GhostButton(ctk.CTkButton):
    """Botao ghost (aparencia minimalista)."""

    def __init__(self, master, text: str, command=None, **kwargs):
        super().__init__(
            master,
            text=text,
            command=command,
            height=32,
            font=DPITheme.FONT_LABEL,
            fg_color="transparent",
            hover_color=DPITheme.BORDER_LIGHT[0],
            text_color=DPITheme.ACCENT[0],
            corner_radius=DPITheme.RADIUS_SM,
            **kwargs,
        )


class ResultCard(ctk.CTkFrame):
    """Card de resultado com custo total estilo macOS."""

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=DPITheme.SURFACE_CARD[0],
            corner_radius=DPITheme.RADIUS_MD,
            border_width=1,
            border_color=DPITheme.BORDER[0],
            **kwargs,
        )

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)

        ctk.CTkLabel(
            self,
            text="Custo Total",
            font=DPITheme.FONT_LABEL,
            text_color=DPITheme.TEXT_SECONDARY[0],
        ).grid(row=0, column=0, padx=20, pady=(14, 0), sticky="w")

        self.label_valor = ctk.CTkLabel(
            self,
            text="R$ 0,00",
            font=(DPITheme.FONT_FAMILY, 26, "bold"),
            text_color=DPITheme.TEXT_PRIMARY[0],
        )
        self.label_valor.grid(row=1, column=0, padx=20, pady=(0, 14), sticky="w")

        self.label_detalhes = ctk.CTkLabel(
            self,
            text="",
            font=DPITheme.FONT_SMALL,
            text_color=DPITheme.TEXT_SECONDARY[0],
        )
        self.label_detalhes.grid(
            row=1, column=1, padx=20, pady=(0, 14), sticky="e"
        )

    def set_valor(self, custo_centavos: int):
        self.label_valor.configure(text=DPITheme.formatar_reais(custo_centavos))

    def set_detalhes(self, texto: str):
        self.label_detalhes.configure(text=texto)
