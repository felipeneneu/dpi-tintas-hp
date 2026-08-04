import tkinter as tk
import customtkinter as ctk
from config.theme import DPITheme
from views.components import ColorCard, PrimaryButton, SecondaryButton, ResultCard


class MainView(ctk.CTk):
    """Janela principal do DPI Tintas HP - estilo macOS."""

    def __init__(self):
        super().__init__()

        self.title("DPI Tintas HP")
        self.geometry("960x860")
        self.minsize(768, 640)
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
        self._callback_gerenciar_pedidos = None
        self._callback_gerenciar_bobinas = None
        self._callback_iniciar_ciclo = None
        self._callback_finalizar_ciclo = None
        self._callback_buscar = None
        self._callback_relatorio = None

        self._ciclo_ativo = False
        self._timer_segundos = 0
        self._timer_job = None

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

        menu_buscar = tk.Menu(self.menu_bar, tearoff=0)
        menu_buscar.add_command(
            label="Buscar Historico",
            command=self._on_buscar,
        )
        self.menu_bar.add_cascade(label="Buscar", menu=menu_buscar)

        menu_relatorios = tk.Menu(self.menu_bar, tearoff=0)
        menu_relatorios.add_command(
            label="Relatorio Diario",
            command=lambda: self._on_relatorio("diario"),
        )
        menu_relatorios.add_command(
            label="Relatorio Semanal",
            command=lambda: self._on_relatorio("semanal"),
        )
        menu_relatorios.add_separator()
        menu_relatorios.add_command(
            label="Exportar PDF",
            command=lambda: self._on_exportar("pdf"),
        )
        menu_relatorios.add_command(
            label="Exportar Excel",
            command=lambda: self._on_exportar("excel"),
        )
        self.menu_bar.add_cascade(label="Relatorios", menu=menu_relatorios)

    def _toggle_theme(self):
        current = ctk.get_appearance_mode()
        new_mode = "Dark" if current == "Light" else "Light"
        ctk.set_appearance_mode(new_mode)

    def _criar_layout(self):
        self.main_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=DPITheme.BG_WINDOW[0],
        )
        self.main_frame.pack(fill="both", expand=True)

        self._criar_header()
        self._criar_secao_pedido()
        self._criar_secao_bobina()
        self._criar_secao_ciclo()
        self._criar_secao_tintas()
        self._criar_botao_calcular()
        self._criar_resultado()
        self._criar_secao_relatorios()
        self._criar_footer()

    def _criar_header(self):
        header = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header.pack(fill="x", padx=DPITheme.SPACING_XL, pady=(DPITheme.SPACING_LG, DPITheme.SPACING_MD))

        import os
        from PIL import Image

        logo_path = DPITheme.LOGO_PATH
        if os.path.exists(logo_path):
            try:
                img = Image.open(logo_path)
                logo = ctk.CTkImage(
                    light_image=img,
                    dark_image=img,
                    size=(36, 36),
                )
                ctk.CTkLabel(header, image=logo, text="").pack(
                    side="left", padx=(0, 12)
                )
            except Exception:
                pass

        textos = ctk.CTkFrame(header, fg_color="transparent")
        textos.pack(side="left")

        ctk.CTkLabel(
            textos,
            text="DPI Tintas HP",
            font=DPITheme.FONT_TITLE,
            text_color=DPITheme.TEXT_PRIMARY[0],
        ).pack(anchor="w")

        ctk.CTkLabel(
            textos,
            text="Controle de Consumo - HP Latex 330",
            font=DPITheme.FONT_SMALL,
            text_color=DPITheme.TEXT_SECONDARY[0],
        ).pack(anchor="w")

        badge_frame = ctk.CTkFrame(header, fg_color="transparent")
        badge_frame.pack(side="right")

        for cor, info in DPITheme.CORES.items():
            badge = ctk.CTkFrame(
                badge_frame,
                width=28,
                height=28,
                fg_color=info["hex"],
                corner_radius=DPITheme.RADIUS_CIRCLE,
            )
            badge.pack(side="left", padx=2)
            badge.pack_propagate(False)

            ctk.CTkLabel(
                badge,
                text=cor,
                font=(DPITheme.FONT_FAMILY, 9, "bold"),
                text_color=info["text_color"],
            ).pack(expand=True)

    def _criar_secao_pedido(self):
        secao = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        secao.pack(fill="x", padx=DPITheme.SPACING_XL, pady=(DPITheme.SPACING_SM, 0))

        header = ctk.CTkFrame(secao, fg_color="transparent")
        header.pack(fill="x")
        ctk.CTkLabel(
            header,
            text="Pedido",
            font=DPITheme.FONT_SUBTITLE,
            text_color=DPITheme.TEXT_PRIMARY[0],
        ).pack(anchor="w")

        card = ctk.CTkFrame(
            secao,
            fg_color=DPITheme.SURFACE_CARD[0],
            corner_radius=DPITheme.RADIUS_MD,
            border_width=1,
            border_color=DPITheme.BORDER[0],
        )
        card.pack(fill="x", pady=(DPITheme.SPACING_SM, 0))

        campos = ctk.CTkFrame(card, fg_color="transparent")
        campos.pack(fill="x", padx=DPITheme.SPACING_MD, pady=DPITheme.SPACING_MD)
        campos.columnconfigure(1, weight=1)
        campos.columnconfigure(3, weight=1)

        ctk.CTkLabel(
            campos,
            text="Numero",
            font=DPITheme.FONT_LABEL,
            text_color=DPITheme.TEXT_SECONDARY[0],
        ).grid(row=0, column=0, padx=(0, 8), sticky="w")

        self.entry_pedido_num = ctk.CTkEntry(
            campos,
            height=36,
            font=DPITheme.FONT_VALUE,
            placeholder_text="OS-2024-001",
            border_color=DPITheme.BORDER[0],
            fg_color=DPITheme.SURFACE_INPUT[0],
            corner_radius=DPITheme.RADIUS_SM,
        )
        self.entry_pedido_num.grid(row=0, column=1, sticky="ew")

        ctk.CTkLabel(
            campos,
            text="Nome",
            font=DPITheme.FONT_LABEL,
            text_color=DPITheme.TEXT_SECONDARY[0],
        ).grid(row=0, column=2, padx=(DPITheme.SPACING_MD, 8), sticky="w")

        self.entry_pedido_nome = ctk.CTkEntry(
            campos,
            height=36,
            font=DPITheme.FONT_VALUE,
            placeholder_text="Descricao (opcional)",
            border_color=DPITheme.BORDER[0],
            fg_color=DPITheme.SURFACE_INPUT[0],
            corner_radius=DPITheme.RADIUS_SM,
        )
        self.entry_pedido_nome.grid(row=0, column=3, sticky="ew")

        self.btn_gerenciar_pedidos = SecondaryButton(
            campos,
            text="Gerenciar",
            width=100,
            command=self._on_gerenciar_pedidos,
        )
        self.btn_gerenciar_pedidos.grid(row=0, column=4, padx=(DPITheme.SPACING_MD, 0))

    def _criar_secao_bobina(self):
        secao = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        secao.pack(fill="x", padx=DPITheme.SPACING_XL, pady=(DPITheme.SPACING_SM, 0))

        header = ctk.CTkFrame(secao, fg_color="transparent")
        header.pack(fill="x")
        ctk.CTkLabel(
            header,
            text="Bobina",
            font=DPITheme.FONT_SUBTITLE,
            text_color=DPITheme.TEXT_PRIMARY[0],
        ).pack(anchor="w")

        card = ctk.CTkFrame(
            secao,
            fg_color=DPITheme.SURFACE_CARD[0],
            corner_radius=DPITheme.RADIUS_MD,
            border_width=1,
            border_color=DPITheme.BORDER[0],
        )
        card.pack(fill="x", pady=(DPITheme.SPACING_SM, 0))

        campos = ctk.CTkFrame(card, fg_color="transparent")
        campos.pack(fill="x", padx=DPITheme.SPACING_MD, pady=DPITheme.SPACING_MD)
        campos.columnconfigure(1, weight=1)

        ctk.CTkLabel(
            campos,
            text="Bobina Ativa",
            font=DPITheme.FONT_LABEL,
            text_color=DPITheme.TEXT_SECONDARY[0],
        ).grid(row=0, column=0, padx=(0, 8), sticky="w")

        self.combo_bobina = ctk.CTkComboBox(
            campos,
            height=36,
            font=DPITheme.FONT_VALUE,
            values=["Nenhuma bobina cadastrada"],
            border_color=DPITheme.BORDER[0],
            fg_color=DPITheme.SURFACE_INPUT[0],
            button_color=DPITheme.ACCENT[0],
            button_hover_color=DPITheme.ACCENT_HOVER[0],
            dropdown_fg_color=DPITheme.SURFACE_CARD[0],
            corner_radius=DPITheme.RADIUS_SM,
        )
        self.combo_bobina.grid(row=0, column=1, sticky="ew")

        self.label_bobina_detalhes = ctk.CTkLabel(
            campos,
            text="",
            font=DPITheme.FONT_SMALL,
            text_color=DPITheme.TEXT_SECONDARY[0],
        )
        self.label_bobina_detalhes.grid(row=0, column=2, padx=(DPITheme.SPACING_MD, 0), sticky="w")

        self.btn_gerenciar_bobinas = SecondaryButton(
            campos,
            text="Gerenciar",
            width=100,
            command=self._on_gerenciar_bobinas,
        )
        self.btn_gerenciar_bobinas.grid(row=0, column=3, padx=(DPITheme.SPACING_MD, 0))

    def _criar_secao_ciclo(self):
        secao = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        secao.pack(fill="x", padx=DPITheme.SPACING_XL, pady=(DPITheme.SPACING_SM, 0))

        header = ctk.CTkFrame(secao, fg_color="transparent")
        header.pack(fill="x")
        ctk.CTkLabel(
            header,
            text="Ciclo de Impressao",
            font=DPITheme.FONT_SUBTITLE,
            text_color=DPITheme.TEXT_PRIMARY[0],
        ).pack(anchor="w")

        card = ctk.CTkFrame(
            secao,
            fg_color=DPITheme.SURFACE_CARD[0],
            corner_radius=DPITheme.RADIUS_MD,
            border_width=1,
            border_color=DPITheme.BORDER[0],
        )
        card.pack(fill="x", pady=(DPITheme.SPACING_SM, 0))

        campos = ctk.CTkFrame(card, fg_color="transparent")
        campos.pack(fill="x", padx=DPITheme.SPACING_MD, pady=DPITheme.SPACING_MD)
        campos.columnconfigure(1, weight=1)

        ctk.CTkLabel(
            campos,
            text="Arquivo",
            font=DPITheme.FONT_LABEL,
            text_color=DPITheme.TEXT_SECONDARY[0],
        ).grid(row=0, column=0, padx=(0, 8), sticky="w")

        self.entry_arquivo = ctk.CTkEntry(
            campos,
            height=36,
            font=DPITheme.FONT_VALUE,
            placeholder_text="Nome do arquivo impresso",
            border_color=DPITheme.BORDER[0],
            fg_color=DPITheme.SURFACE_INPUT[0],
            corner_radius=DPITheme.RADIUS_SM,
        )
        self.entry_arquivo.grid(row=0, column=1, sticky="ew")

        self.btn_iniciar = ctk.CTkButton(
            campos,
            text="Iniciar",
            width=90,
            height=36,
            font=DPITheme.FONT_BUTTON,
            fg_color=DPITheme.SUCCESS[0],
            hover_color=DPITheme.SUCCESS_HOVER[0],
            corner_radius=DPITheme.RADIUS_SM,
            command=self._on_iniciar_ciclo,
        )
        self.btn_iniciar.grid(row=0, column=2, padx=(DPITheme.SPACING_MD, 6))

        self.btn_finalizar = ctk.CTkButton(
            campos,
            text="Finalizar",
            width=90,
            height=36,
            font=DPITheme.FONT_BUTTON,
            fg_color=DPITheme.WARNING[0],
            hover_color=DPITheme.WARNING_HOVER[0],
            corner_radius=DPITheme.RADIUS_SM,
            command=self._on_finalizar_ciclo,
            state="disabled",
        )
        self.btn_finalizar.grid(row=0, column=3, padx=(6, 0))

        self.label_timer = ctk.CTkLabel(
            campos,
            text="00:00:00",
            font=(DPITheme.FONT_MONO, 14, "bold"),
            text_color=DPITheme.TEXT_SECONDARY[0],
        )
        self.label_timer.grid(row=0, column=4, padx=(DPITheme.SPACING_MD, 0))

    def _criar_secao_tintas(self):
        secao = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        secao.pack(fill="x", padx=DPITheme.SPACING_XL, pady=(DPITheme.SPACING_MD, 0))

        header = ctk.CTkFrame(secao, fg_color="transparent")
        header.pack(fill="x")
        ctk.CTkLabel(
            header,
            text="Niveis de Tinta",
            font=DPITheme.FONT_SUBTITLE,
            text_color=DPITheme.TEXT_PRIMARY[0],
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Informe o nivel inicial e final de cada cor em mililitros",
            font=DPITheme.FONT_SMALL,
            text_color=DPITheme.TEXT_SECONDARY[0],
        ).pack(anchor="w", pady=(2, 0))

        self.cards_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.cards_frame.pack(fill="x", padx=DPITheme.SPACING_XL, pady=(DPITheme.SPACING_SM, 0))

        self.cards = {}
        cores_lista = list(DPITheme.CORES.items())

        row1 = ctk.CTkFrame(self.cards_frame, fg_color="transparent")
        row1.pack(fill="x", pady=3)
        row1.columnconfigure((0, 1, 2), weight=1)
        for i, (cor, info) in enumerate(cores_lista[:3]):
            card = ColorCard(row1, cor, info)
            card.grid(row=0, column=i, padx=3, sticky="ew")
            self.cards[cor] = card

        row2 = ctk.CTkFrame(self.cards_frame, fg_color="transparent")
        row2.pack(fill="x", pady=3)
        row2.columnconfigure((0, 1, 2), weight=1)
        for i, (cor, info) in enumerate(cores_lista[3:6]):
            card = ColorCard(row2, cor, info)
            card.grid(row=0, column=i, padx=3, sticky="ew")
            self.cards[cor] = card

        row3 = ctk.CTkFrame(self.cards_frame, fg_color="transparent")
        row3.pack(fill="x", pady=3)
        card = ColorCard(row3, cores_lista[6][0], cores_lista[6][1])
        card.pack(anchor="w", padx=3)
        self.cards[cores_lista[6][0]] = card

    def _criar_botao_calcular(self):
        container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        container.pack(fill="x", padx=DPITheme.SPACING_XL, pady=DPITheme.SPACING_MD)

        self.btn_calcular = PrimaryButton(
            container,
            text="CALCULAR & REGISTRAR",
            command=self._on_calcular,
        )
        self.btn_calcular.pack(fill="x")

    def _criar_resultado(self):
        self.resultado = ResultCard(self.main_frame)
        self.resultado.pack(fill="x", padx=DPITheme.SPACING_XL, pady=(0, DPITheme.SPACING_MD))

    def _criar_secao_relatorios(self):
        secao = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        secao.pack(fill="x", padx=DPITheme.SPACING_XL, pady=(DPITheme.SPACING_SM, 0))

        header = ctk.CTkFrame(secao, fg_color="transparent")
        header.pack(fill="x")
        ctk.CTkLabel(
            header,
            text="Relatorios",
            font=DPITheme.FONT_SUBTITLE,
            text_color=DPITheme.TEXT_PRIMARY[0],
        ).pack(anchor="w")

        card = ctk.CTkFrame(
            secao,
            fg_color=DPITheme.SURFACE_CARD[0],
            corner_radius=DPITheme.RADIUS_MD,
            border_width=1,
            border_color=DPITheme.BORDER[0],
        )
        card.pack(fill="x", pady=(DPITheme.SPACING_SM, 0))

        botoes = ctk.CTkFrame(card, fg_color="transparent")
        botoes.pack(fill="x", padx=DPITheme.SPACING_MD, pady=DPITheme.SPACING_MD)

        SecondaryButton(
            botoes,
            text="Diario",
            width=90,
            command=lambda: self._on_relatorio("diario"),
        ).pack(side="left", padx=(0, 6))

        SecondaryButton(
            botoes,
            text="Semanal",
            width=90,
            command=lambda: self._on_relatorio("semanal"),
        ).pack(side="left", padx=(0, 6))

        ctk.CTkFrame(botoes, width=1, height=24, fg_color=DPITheme.DIVIDER[0]).pack(
            side="left", padx=DPITheme.SPACING_SM
        )

        ctk.CTkButton(
            botoes,
            text="PDF",
            width=60,
            height=32,
            font=DPITheme.FONT_LABEL,
            fg_color=DPITheme.DANGER[0],
            hover_color=DPITheme.DANGER_HOVER[0],
            corner_radius=DPITheme.RADIUS_SM,
            command=lambda: self._on_exportar("pdf"),
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            botoes,
            text="Excel",
            width=60,
            height=32,
            font=DPITheme.FONT_LABEL,
            fg_color=DPITheme.SUCCESS[0],
            hover_color=DPITheme.SUCCESS_HOVER[0],
            corner_radius=DPITheme.RADIUS_SM,
            command=lambda: self._on_exportar("excel"),
        ).pack(side="left")

    def _criar_footer(self):
        footer = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        footer.pack(fill="x", padx=DPITheme.SPACING_XL, pady=(DPITheme.SPACING_MD, DPITheme.SPACING_LG))

        ctk.CTkLabel(
            footer,
            text="DPI Visual - Solucoes em Impressao Digital",
            font=DPITheme.FONT_SMALL,
            text_color=DPITheme.TEXT_TERTIARY[0],
        ).pack(anchor="center")

    def _iniciar_timer(self):
        self._ciclo_ativo = True
        self._timer_segundos = 0
        self._atualizar_timer()

    def _atualizar_timer(self):
        if not self._ciclo_ativo:
            return
        horas = self._timer_segundos // 3600
        minutos = (self._timer_segundos % 3600) // 60
        segundos = self._timer_segundos % 60
        self.label_timer.configure(
            text=f"{horas:02d}:{minutos:02d}:{segundos:02d}"
        )
        self._timer_segundos += 1
        self._timer_job = self.after(1000, self._atualizar_timer)

    def _parar_timer(self):
        self._ciclo_ativo = False
        if self._timer_job:
            self.after_cancel(self._timer_job)
            self._timer_job = None

    def _on_calcular(self):
        if self._callback_calcular:
            self._callback_calcular()

    def _on_configurar(self):
        if self._callback_configurar:
            self._callback_configurar()

    def _on_exportar(self, formato: str):
        if self._callback_exportar:
            self._callback_exportar(formato)

    def _on_gerenciar_pedidos(self):
        if self._callback_gerenciar_pedidos:
            self._callback_gerenciar_pedidos()

    def _on_gerenciar_bobinas(self):
        if self._callback_gerenciar_bobinas:
            self._callback_gerenciar_bobinas()

    def _on_iniciar_ciclo(self):
        self._iniciar_timer()
        self.btn_iniciar.configure(state="disabled")
        self.btn_finalizar.configure(state="normal")
        if self._callback_iniciar_ciclo:
            self._callback_iniciar_ciclo()

    def _on_finalizar_ciclo(self):
        self._parar_timer()
        self.btn_iniciar.configure(state="normal")
        self.btn_finalizar.configure(state="disabled")
        if self._callback_finalizar_ciclo:
            self._callback_finalizar_ciclo()

    def _on_buscar(self):
        if self._callback_buscar:
            self._callback_buscar()

    def _on_relatorio(self, tipo: str):
        if self._callback_relatorio:
            self._callback_relatorio(tipo)

    def set_callbacks(
        self,
        calcular=None,
        configurar=None,
        exportar=None,
        gerenciar_pedidos=None,
        gerenciar_bobinas=None,
        iniciar_ciclo=None,
        finalizar_ciclo=None,
        buscar=None,
        relatorio=None,
    ):
        self._callback_calcular = calcular
        self._callback_configurar = configurar
        self._callback_exportar = exportar
        self._callback_gerenciar_pedidos = gerenciar_pedidos
        self._callback_gerenciar_bobinas = gerenciar_bobinas
        self._callback_iniciar_ciclo = iniciar_ciclo
        self._callback_finalizar_ciclo = finalizar_ciclo
        self._callback_buscar = buscar
        self._callback_relatorio = relatorio

    def set_reabastecer_callbacks(self, callback):
        for card in self.cards.values():
            card.set_reabastecer_callback(callback)

    def get_niveis(self) -> dict:
        niveis = {}
        for cor, card in self.cards.items():
            niveis[cor] = card.get_niveis()
        return niveis

    def get_pedido(self) -> dict:
        return {
            "numero": self.entry_pedido_num.get().strip(),
            "nome": self.entry_pedido_nome.get().strip(),
        }

    def get_bobina_selecionada(self) -> str:
        return self.combo_bobina.get()

    def get_arquivo(self) -> str:
        return self.entry_arquivo.get().strip()

    def get_duracao(self) -> int:
        return self._timer_segundos

    def set_bobinas(self, bobinas: list[dict], atual: str = ""):
        valores = [b["nome"] for b in bobinas] if bobinas else ["Nenhuma bobina cadastrada"]
        self.combo_bobina.configure(values=valores)
        if atual:
            self.combo_bobina.set(atual)
        elif valores:
            self.combo_bobina.set(valores[0])

    def set_bobina_detalhes(self, texto: str):
        self.label_bobina_detalhes.configure(text=texto)

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

    def limpar_campos(self):
        self.entry_pedido_num.delete(0, "end")
        self.entry_pedido_nome.delete(0, "end")
        self.entry_arquivo.delete(0, "end")
        self._parar_timer()
        self.label_timer.configure(text="00:00:00")
        self.btn_iniciar.configure(state="normal")
        self.btn_finalizar.configure(state="disabled")
        for card in self.cards.values():
            card.set_nivel_atual(0.0)
            card.set_nivel_final(0.0)
        self.resultado.set_valor(0)
        self.resultado.set_detalhes("")

    def mostrar_aviso(self, titulo: str, mensagem: str):
        dialog = ctk.CTkToplevel(self)
        dialog.title(titulo)
        dialog.geometry("380x180")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(fg_color=DPITheme.BG_WINDOW[0])

        ctk.CTkLabel(
            dialog,
            text=mensagem,
            font=DPITheme.FONT_BODY,
            text_color=DPITheme.TEXT_PRIMARY[0],
            wraplength=340,
        ).pack(expand=True, padx=20)

        ctk.CTkButton(
            dialog,
            text="OK",
            command=dialog.destroy,
            fg_color=DPITheme.ACCENT[0],
            hover_color=DPITheme.ACCENT_HOVER[0],
            width=80,
            height=32,
            corner_radius=DPITheme.RADIUS_SM,
        ).pack(pady=(0, 16))

    def mostrar_sucesso(self, mensagem: str):
        self.mostrar_aviso("Sucesso", mensagem)
