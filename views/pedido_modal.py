import customtkinter as ctk
from config.theme import DPITheme


class PedidoModal(ctk.CTkToplevel):
    """Modal para gerenciamento de pedidos - estilo macOS."""

    def __init__(self, master, pedidos: list[dict]):
        super().__init__(master)

        self.title("Gerenciar Pedidos")
        self.geometry("520x450")
        self.transient(master)
        self.grab_set()
        self.configure(fg_color=DPITheme.BG_WINDOW[0])

        self.pedidos = pedidos if pedidos else []
        self.selecionada_index = None
        self.resultado = None

        self._criar_layout()

    def _criar_layout(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=DPITheme.SPACING_LG, pady=(DPITheme.SPACING_LG, DPITheme.SPACING_SM))

        ctk.CTkLabel(
            header,
            text="Gerenciar Pedidos",
            font=DPITheme.FONT_TITLE,
            text_color=DPITheme.TEXT_PRIMARY[0],
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Adicione, edite ou remova pedidos",
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

        if not self.pedidos:
            ctk.CTkLabel(
                self.lista_frame,
                text="Nenhum pedido cadastrado",
                font=DPITheme.FONT_LABEL,
                text_color=DPITheme.TEXT_SECONDARY[0],
            ).pack(pady=24)
            return

        header = ctk.CTkFrame(self.lista_frame, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(8, 4))

        for texto in ["Numero", "Nome"]:
            ctk.CTkLabel(
                header,
                text=texto,
                font=DPITheme.FONT_SMALL,
                text_color=DPITheme.TEXT_SECONDARY[0],
                width=160,
            ).pack(side="left", padx=4)

        for idx, pedido in enumerate(self.pedidos):
            linha = ctk.CTkFrame(
                self.lista_frame,
                fg_color="transparent",
                height=32,
            )
            linha.pack(fill="x", padx=10, pady=1)

            ctk.CTkLabel(
                linha,
                text=pedido.get("numero", ""),
                font=DPITheme.FONT_BODY,
                text_color=DPITheme.TEXT_PRIMARY[0],
                width=160,
            ).pack(side="left", padx=4)

            ctk.CTkLabel(
                linha,
                text=pedido.get("nome", ""),
                font=DPITheme.FONT_BODY,
                text_color=DPITheme.TEXT_PRIMARY[0],
                width=160,
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
            text="Novo Pedido",
            font=DPITheme.FONT_LABEL,
            text_color=DPITheme.TEXT_PRIMARY[0],
        ).pack(anchor="w", padx=12, pady=(8, 4))

        campos = ctk.CTkFrame(form, fg_color="transparent")
        campos.pack(fill="x", padx=12, pady=(0, 8))
        campos.columnconfigure(1, weight=1)
        campos.columnconfigure(3, weight=1)

        ctk.CTkLabel(campos, text="Numero", font=DPITheme.FONT_SMALL, text_color=DPITheme.TEXT_SECONDARY[0]).grid(row=0, column=0, padx=(0, 4), sticky="w")
        self.entry_numero = ctk.CTkEntry(campos, height=30, font=DPITheme.FONT_BODY, placeholder_text="Ex: 12345", border_color=DPITheme.BORDER[0], fg_color=DPITheme.SURFACE_INPUT[0], corner_radius=DPITheme.RADIUS_SM)
        self.entry_numero.grid(row=0, column=1, sticky="ew", padx=(0, 8))

        ctk.CTkLabel(campos, text="Nome", font=DPITheme.FONT_SMALL, text_color=DPITheme.TEXT_SECONDARY[0]).grid(row=0, column=2, padx=(0, 4), sticky="w")
        self.entry_nome = ctk.CTkEntry(campos, height=30, font=DPITheme.FONT_BODY, placeholder_text="Descricao do pedido", border_color=DPITheme.BORDER[0], fg_color=DPITheme.SURFACE_INPUT[0], corner_radius=DPITheme.RADIUS_SM)
        self.entry_nome.grid(row=0, column=3, sticky="ew")

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
        pedido = {
            "numero": self.entry_numero.get().strip(),
            "nome": self.entry_nome.get().strip(),
        }

        if not pedido["numero"]:
            return

        if self.selecionada_index is not None:
            self.pedidos[self.selecionada_index] = pedido
            self.selecionada_index = None
            self.btn_adicionar.configure(text="Adicionar")
        else:
            self.pedidos.append(pedido)

        self._limpar_formulario()
        self._atualizar_lista()

    def _editar(self, index: int):
        if 0 <= index < len(self.pedidos):
            self.selecionada_index = index
            pedido = self.pedidos[index]
            self._limpar_formulario()
            self.entry_numero.insert(0, pedido.get("numero", ""))
            self.entry_nome.insert(0, pedido.get("nome", ""))
            self.btn_adicionar.configure(text="Atualizar")

    def _remover(self, index: int):
        if 0 <= index < len(self.pedidos):
            self.pedidos.pop(index)
            if self.selecionada_index == index:
                self.selecionada_index = None
                self.btn_adicionar.configure(text="Adicionar")
            elif self.selecionada_index is not None and self.selecionada_index > index:
                self.selecionada_index -= 1
            self._atualizar_lista()

    def _limpar_formulario(self):
        self.entry_numero.delete(0, "end")
        self.entry_nome.delete(0, "end")

    def _salvar(self):
        self.resultado = self.pedidos
        self.destroy()

    def _cancelar(self):
        self.resultado = None
        self.destroy()

    def obter_resultado(self) -> list[dict] | None:
        self.wait_window()
        return self.resultado
