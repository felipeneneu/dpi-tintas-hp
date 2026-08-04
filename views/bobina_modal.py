import customtkinter as ctk
from config.theme import DPITheme


class BobinaModal(ctk.CTkToplevel):
    """Modal para gerenciamento de bobinas - estilo macOS."""

    def __init__(self, master, bobinas: list[dict]):
        super().__init__(master)

        self.title("Gerenciar Bobinas")
        self.geometry("560x480")
        self.transient(master)
        self.grab_set()
        self.configure(fg_color=DPITheme.BG_WINDOW[0])

        self.bobinas = bobinas if bobinas else []
        self.selecionada_index = None
        self.resultado = None

        self._criar_layout()

    def _criar_layout(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=DPITheme.SPACING_LG, pady=(DPITheme.SPACING_LG, DPITheme.SPACING_SM))

        ctk.CTkLabel(
            header,
            text="Gerenciar Bobinas",
            font=DPITheme.FONT_TITLE,
            text_color=DPITheme.TEXT_PRIMARY[0],
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Adicione, edite ou remova bobinas",
            font=DPITheme.FONT_SMALL,
            text_color=DPITheme.TEXT_SECONDARY[0],
        ).pack(anchor="w", pady=(2, 0))

        self._criar_lista()
        self._criar_formulario()

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
            text="OK",
            width=100,
            height=36,
            font=DPITheme.FONT_LABEL,
            fg_color=DPITheme.ACCENT[0],
            hover_color=DPITheme.ACCENT_HOVER[0],
            corner_radius=DPITheme.RADIUS_SM,
            command=self._salvar,
        ).pack(side="right")

    def _criar_lista(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=DPITheme.SPACING_LG, pady=(0, DPITheme.SPACING_SM))

        self.lista_frame = ctk.CTkScrollableFrame(
            container,
            fg_color=DPITheme.SURFACE_CARD[0],
            corner_radius=DPITheme.RADIUS_MD,
            border_width=1,
            border_color=DPITheme.BORDER[0],
        )
        self.lista_frame.pack(fill="both", expand=True)

        self._atualizar_lista()

    def _atualizar_lista(self):
        for widget in self.lista_frame.winfo_children():
            widget.destroy()

        if not self.bobinas:
            ctk.CTkLabel(
                self.lista_frame,
                text="Nenhuma bobina cadastrada",
                font=DPITheme.FONT_LABEL,
                text_color=DPITheme.TEXT_SECONDARY[0],
            ).pack(pady=24)
            return

        header = ctk.CTkFrame(self.lista_frame, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(8, 4))

        for texto in ["Nome", "Tamanho", "Material", "Tipo"]:
            ctk.CTkLabel(
                header,
                text=texto,
                font=DPITheme.FONT_SMALL,
                text_color=DPITheme.TEXT_SECONDARY[0],
                width=110,
            ).pack(side="left", padx=4)

        for idx, bobina in enumerate(self.bobinas):
            linha = ctk.CTkFrame(
                self.lista_frame,
                fg_color="transparent",
                height=32,
            )
            linha.pack(fill="x", padx=10, pady=1)

            for campo in ["nome", "tamanho", "material", "tipo"]:
                ctk.CTkLabel(
                    linha,
                    text=bobina.get(campo, ""),
                    font=DPITheme.FONT_BODY,
                    text_color=DPITheme.TEXT_PRIMARY[0],
                    width=110,
                ).pack(side="left", padx=4)

            ctk.CTkButton(
                linha,
                text="Editar",
                width=56,
                height=26,
                font=DPITheme.FONT_SMALL,
                fg_color="transparent",
                hover_color=DPITheme.BORDER_LIGHT[0],
                text_color=DPITheme.ACCENT[0],
                corner_radius=DPITheme.RADIUS_SM,
                command=lambda i=idx: self._editar(i),
            ).pack(side="right", padx=2)

            ctk.CTkButton(
                linha,
                text="X",
                width=26,
                height=26,
                font=DPITheme.FONT_SMALL,
                fg_color="transparent",
                hover_color=DPITheme.DANGER[0],
                text_color=DPITheme.DANGER[0],
                corner_radius=DPITheme.RADIUS_SM,
                command=lambda i=idx: self._remover(i),
            ).pack(side="right", padx=2)

    def _criar_formulario(self):
        form = ctk.CTkFrame(
            self,
            fg_color=DPITheme.SURFACE_CARD[0],
            corner_radius=DPITheme.RADIUS_MD,
            border_width=1,
            border_color=DPITheme.BORDER[0],
        )
        form.pack(fill="x", padx=DPITheme.SPACING_LG, pady=(0, DPITheme.SPACING_SM))

        ctk.CTkLabel(
            form,
            text="Nova Bobina",
            font=DPITheme.FONT_LABEL,
            text_color=DPITheme.TEXT_PRIMARY[0],
        ).pack(anchor="w", padx=12, pady=(8, 4))

        campos = ctk.CTkFrame(form, fg_color="transparent")
        campos.pack(fill="x", padx=12, pady=(0, 8))
        campos.columnconfigure(1, weight=1)
        campos.columnconfigure(3, weight=1)

        ctk.CTkLabel(campos, text="Nome", font=DPITheme.FONT_SMALL, text_color=DPITheme.TEXT_SECONDARY[0]).grid(row=0, column=0, padx=(0, 4), sticky="w")
        self.entry_nome = ctk.CTkEntry(campos, height=30, font=DPITheme.FONT_BODY, placeholder_text="Ex: Bobina 1", border_color=DPITheme.BORDER[0], fg_color=DPITheme.SURFACE_INPUT[0], corner_radius=DPITheme.RADIUS_SM)
        self.entry_nome.grid(row=0, column=1, sticky="ew", padx=(0, 8))

        ctk.CTkLabel(campos, text="Tamanho", font=DPITheme.FONT_SMALL, text_color=DPITheme.TEXT_SECONDARY[0]).grid(row=0, column=2, padx=(0, 4), sticky="w")
        self.entry_tamanho = ctk.CTkEntry(campos, height=30, font=DPITheme.FONT_BODY, placeholder_text="Ex: 100x150cm", border_color=DPITheme.BORDER[0], fg_color=DPITheme.SURFACE_INPUT[0], corner_radius=DPITheme.RADIUS_SM)
        self.entry_tamanho.grid(row=0, column=3, sticky="ew")

        ctk.CTkLabel(campos, text="Material", font=DPITheme.FONT_SMALL, text_color=DPITheme.TEXT_SECONDARY[0]).grid(row=1, column=0, padx=(0, 4), sticky="w", pady=(4, 0))
        self.entry_material = ctk.CTkEntry(campos, height=30, font=DPITheme.FONT_BODY, placeholder_text="Ex: Vinil", border_color=DPITheme.BORDER[0], fg_color=DPITheme.SURFACE_INPUT[0], corner_radius=DPITheme.RADIUS_SM)
        self.entry_material.grid(row=1, column=1, sticky="ew", padx=(0, 8), pady=(4, 0))

        ctk.CTkLabel(campos, text="Tipo", font=DPITheme.FONT_SMALL, text_color=DPITheme.TEXT_SECONDARY[0]).grid(row=1, column=2, padx=(0, 4), sticky="w", pady=(4, 0))
        self.entry_tipo = ctk.CTkEntry(campos, height=30, font=DPITheme.FONT_BODY, placeholder_text="Ex: Brilho", border_color=DPITheme.BORDER[0], fg_color=DPITheme.SURFACE_INPUT[0], corner_radius=DPITheme.RADIUS_SM)
        self.entry_tipo.grid(row=1, column=3, sticky="ew", pady=(4, 0))

        self.btn_adicionar = ctk.CTkButton(
            form,
            text="Adicionar",
            width=90,
            height=30,
            font=DPITheme.FONT_LABEL,
            fg_color=DPITheme.SUCCESS[0],
            hover_color=DPITheme.SUCCESS_HOVER[0],
            corner_radius=DPITheme.RADIUS_SM,
            command=self._adicionar,
        )
        self.btn_adicionar.pack(anchor="w", padx=12, pady=(0, 8))

    def _adicionar(self):
        bobina = {
            "nome": self.entry_nome.get().strip(),
            "tamanho": self.entry_tamanho.get().strip(),
            "material": self.entry_material.get().strip(),
            "tipo": self.entry_tipo.get().strip(),
        }

        if not bobina["nome"]:
            return

        if self.selecionada_index is not None:
            self.bobinas[self.selecionada_index] = bobina
            self.selecionada_index = None
            self.btn_adicionar.configure(text="Adicionar")
        else:
            self.bobinas.append(bobina)

        self._limpar_formulario()
        self._atualizar_lista()

    def _editar(self, index: int):
        if 0 <= index < len(self.bobinas):
            self.selecionada_index = index
            bobina = self.bobinas[index]
            self._limpar_formulario()
            self.entry_nome.insert(0, bobina.get("nome", ""))
            self.entry_tamanho.insert(0, bobina.get("tamanho", ""))
            self.entry_material.insert(0, bobina.get("material", ""))
            self.entry_tipo.insert(0, bobina.get("tipo", ""))
            self.btn_adicionar.configure(text="Atualizar")

    def _remover(self, index: int):
        if 0 <= index < len(self.bobinas):
            self.bobinas.pop(index)
            if self.selecionada_index == index:
                self.selecionada_index = None
                self.btn_adicionar.configure(text="Adicionar")
            elif self.selecionada_index is not None and self.selecionada_index > index:
                self.selecionada_index -= 1
            self._atualizar_lista()

    def _limpar_formulario(self):
        self.entry_nome.delete(0, "end")
        self.entry_tamanho.delete(0, "end")
        self.entry_material.delete(0, "end")
        self.entry_tipo.delete(0, "end")

    def _salvar(self):
        self.resultado = self.bobinas
        self.destroy()

    def _cancelar(self):
        self.resultado = None
        self.destroy()

    def obter_resultado(self) -> list[dict] | None:
        self.wait_window()
        return self.resultado
