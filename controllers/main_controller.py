import json
import os
from datetime import datetime
from tkinter import filedialog, messagebox

from config.theme import DPITheme
from models.tinta_model import TintaModel
from views.main_view import MainView
from views.config_modal import ConfigModal
from views.bobina_modal import BobinaModal
from views.pedido_modal import PedidoModal


class MainController:
    """Controlador principal - conecta View e Model."""

    def __init__(self):
        self.model = TintaModel()
        self.view = MainView()

        self._pedido_atual_id = None
        self._bobina_atual_id = None
        self._impressao_atual_id = None

        self.view.set_callbacks(
            calcular=self._on_calcular,
            configurar=self._on_configurar,
            exportar=self._on_exportar,
            gerenciar_pedidos=self._on_gerenciar_pedidos_modal,
            gerenciar_bobinas=self._on_gerenciar_bobinas_modal,
            iniciar_ciclo=self._on_iniciar_ciclo,
            finalizar_ciclo=self._on_finalizar_impressao,
            buscar=self._on_buscar_modal,
            relatorio=self._on_gerar_relatorio,
        )
        self.view.set_reabastecer_callbacks(self._on_reabastecer)

        self._carregar_dados_iniciais()

    def _carregar_dados_iniciais(self):
        config = self.model.get_configuracoes()
        for cor, dados in config.items():
            self.view.set_nivel_atual(cor, dados["nivel_atual_ml"])

        ultimo = self.model.get_ultimo_rodagem()
        if ultimo:
            niveis_fim = {cor: ultimo.get(f"{cor.lower()}_fim", 0) for cor in TintaModel.CORES}
            self.view.set_niveis_finais(niveis_fim)
            self.view.set_resultado(ultimo["custo_total_centavos"])

        bobinas = self.model.get_bobinas()
        self.view.set_bobinas(bobinas)

    def _on_reabastecer(self, cor: str):
        self.model.reabastecer(cor)
        config = self.model.get_configuracoes().get(cor, {})
        capacidade = config.get("capacidade_ml", 775.0)
        self.view.set_nivel_atual(cor, capacidade)
        self.view.mostrar_sucesso(
            f"Cartucho {DPITheme.CORES[cor]['name']} reabastecido para {capacidade:.0f}ml!"
        )

    def _on_calcular(self):
        niveis = self.view.get_niveis()

        niveis_ini = {}
        niveis_fim = {}
        for cor in TintaModel.CORES:
            ini, fim = niveis[cor]
            niveis_ini[cor] = ini
            niveis_fim[cor] = fim

        for cor in TintaModel.CORES:
            if niveis_fim[cor] > niveis_ini[cor]:
                self.view.mostrar_aviso(
                    "Erro",
                    f"O nivel final de {DPITheme.CORES[cor]['name']} "
                    f"({niveis_fim[cor]:.1f}ml) nao pode ser maior "
                    f"que o inicial ({niveis_ini[cor]:.1f}ml)!",
                )
                return

        detalhes, custo_total = self.model.calcular_custos(niveis_ini, niveis_fim)

        texto_detalhes = " | ".join(
            [
                f"{cor}: {d['gasto_ml']:.1f}ml = {DPITheme.formatar_reais(d['custo_centavos'])}"
                for cor, d in detalhes.items()
                if d["gasto_ml"] > 0
            ]
        )
        if not texto_detalhes:
            texto_detalhes = "Sem consumo registrado"

        self.view.set_resultado(custo_total, texto_detalhes)

        if self._impressao_atual_id is not None:
            self.model.finalizar_impressao(
                self._impressao_atual_id, niveis_fim, custo_total
            )
            self._impressao_atual_id = None
        else:
            self.model.salvar_impressao(
                pedido_id=self._pedido_atual_id,
                bobina_id=self._bobina_atual_id,
                nome_arquivo="",
                niveis_ini_ml=niveis_ini,
                niveis_fim_ml=niveis_fim,
                custo_total_centavos=custo_total,
            )

        for cor in TintaModel.CORES:
            self.view.set_nivel_atual(cor, niveis_fim[cor])

        proximos = {cor: niveis_fim[cor] for cor in TintaModel.CORES}
        self.view.set_niveis_finais(proximos)

        self.view.mostrar_sucesso(
            f"Impressao registrada!\n\n"
            f"Custo total: {DPITheme.formatar_reais(custo_total)}"
        )

    def _on_configurar(self):
        config = self.model.get_configuracoes()
        modal = ConfigModal(self.view, config)
        resultado = modal.obter_resultado()

        if resultado:
            for cor, dados in resultado.items():
                self.model.atualizar_configuracao(
                    cor, dados["capacidade_ml"], dados["preco_centavos"]
                )
            self.view.mostrar_sucesso("Configuracao salva com sucesso!")

    def _on_exportar(self, formato: str):
        try:
            if formato == "json":
                dados = self.model.exportar_json()
                caminho = filedialog.asksaveasfilename(
                    defaultextension=".json",
                    filetypes=[("JSON", "*.json")],
                    initialfile=f"dpi_tintas_backup_{datetime.now():%Y%m%d_%H%M%S}.json",
                    title="Exportar Backup JSON",
                )
                if caminho:
                    with open(caminho, "w", encoding="utf-8") as f:
                        json.dump(dados, f, indent=2, ensure_ascii=False)
                    self.view.mostrar_sucesso(
                        f"Backup exportado com sucesso!\n\n{caminho}"
                    )

            elif formato == "sql":
                sql = self.model.exportar_sql()
                caminho = filedialog.asksaveasfilename(
                    defaultextension=".sql",
                    filetypes=[("SQL", "*.sql")],
                    initialfile=f"dpi_tintas_backup_{datetime.now():%Y%m%d_%H%M%S}.sql",
                    title="Exportar Backup SQL",
                )
                if caminho:
                    with open(caminho, "w", encoding="utf-8") as f:
                        f.write(sql)
                    self.view.mostrar_sucesso(
                        f"Script SQL exportado com sucesso!\n\n{caminho}"
                    )

        except Exception as e:
            self.view.mostrar_aviso("Erro", f"Falha ao exportar:\n{str(e)}")

    def _on_iniciar_ciclo(self, pedido_id: int | None = None, bobina_id: int | None = None):
        """Inicia um novo ciclo de impressao."""
        self._pedido_atual_id = pedido_id
        self._bobina_atual_id = bobina_id
        niveis_ini = self.model.get_niveis_atuais()
        self._impressao_atual_id = self.model.salvar_impressao(
            pedido_id=pedido_id,
            bobina_id=bobina_id,
            nome_arquivo="",
            niveis_ini_ml=niveis_ini,
            niveis_fim_ml={cor: 0 for cor in TintaModel.CORES},
            custo_total_centavos=0,
        )
        self.view.mostrar_sucesso("Ciclo de impressao iniciado!")

    def _on_finalizar_impressao(self):
        """Finaliza a impressao atual."""
        if self._impressao_atual_id is None:
            self.view.mostrar_aviso("Aviso", "Nenhum ciclo de impressao em andamento!")
            return
        self._on_calcular()

    def _on_gerenciar_pedidos(self):
        """Abre gerenciamento de pedidos."""
        pedidos = self.model.get_pedidos()
        self.view.mostrar_aviso(
            "Pedidos",
            f"Total de pedidos: {len(pedidos)}\n"
            + "\n".join(
                [f"- #{p['numero']}: {p['nome']}" for p in pedidos[:10]]
            )
            if pedidos
            else "Nenhum pedido registrado.",
        )

    def _on_gerenciar_pedidos_modal(self):
        """Abre modal de gerenciamento de pedidos."""
        pedidos = self.model.get_pedidos()
        modal = PedidoModal(self.view, pedidos)
        resultado = modal.obter_resultado()
        if resultado is not None:
            self.model.salvar_pedidos(resultado)
            self.view.mostrar_sucesso("Pedidos atualizados com sucesso!")

    def _on_criar_pedido(self, numero: str, nome: str = ""):
        """Cria um novo pedido."""
        pedido_id = self.model.criar_pedido(numero, nome)
        self._pedido_atual_id = pedido_id
        self.view.mostrar_sucesso(f"Pedido #{numero} criado com sucesso!")

    def _on_gerenciar_bobinas(self):
        """Abre gerenciamento de bobinas."""
        bobinas = self.model.get_bobinas()
        self.view.mostrar_aviso(
            "Bobinas",
            f"Total de bobinas: {len(bobinas)}\n"
            + "\n".join(
                [f"- {b['tamanho']} ({b['material']}) - {b['tipo']}" for b in bobinas[:10]]
            )
            if bobinas
            else "Nenhuma bobina registrada.",
        )

    def _on_gerenciar_bobinas_modal(self):
        """Abre modal de gerenciamento de bobinas."""
        bobinas = self.model.get_bobinas()
        modal = BobinaModal(self.view, bobinas)
        resultado = modal.obter_resultado()
        if resultado is not None:
            self.model.salvar_bobinas(resultado)
            self.view.set_bobinas(resultado)
            self.view.mostrar_sucesso("Bobinas atualizadas com sucesso!")

    def _on_criar_bobina(self, tamanho: str, material: str, tipo: str):
        """Cria uma nova bobina."""
        bobina_id = self.model.criar_bobina(tamanho, material, tipo)
        self._bobina_atual_id = bobina_id
        self.view.mostrar_sucesso(
            f"Bobina {tamanho} ({material}) criada com sucesso!"
        )

    def _on_buscar(self, termo: str):
        """Busca impressoes por termo."""
        resultados = self.model.buscar_impressoes(termo)
        if resultados:
            self.view.mostrar_aviso(
                "Resultados da Busca",
                f"Encontradas {len(resultados)} impressoes:\n"
                + "\n".join(
                    [
                        f"- {r['nome_arquivo']} ({r['data_inicio']})"
                        for r in resultados[:10]
                    ]
                ),
            )
        else:
            self.view.mostrar_aviso("Busca", "Nenhum resultado encontrado.")

    def _on_buscar_modal(self, filtros: dict = None):
        """Busca impressoes com filtros."""
        termo = filtros.get("busca", "") if filtros else ""
        resultados = self.model.buscar_impressoes(termo)
        if resultados:
            self.view.mostrar_aviso(
                "Resultados da Busca",
                f"Encontradas {len(resultados)} impressoes:\n"
                + "\n".join(
                    [
                        f"- {r['nome_arquivo']} ({r['data_inicio']})"
                        for r in resultados[:10]
                    ]
                ),
            )
        else:
            self.view.mostrar_aviso("Busca", "Nenhum resultado encontrado.")

    def _on_gerar_relatorio(self, tipo: str = "diario"):
        """Gera relatorio diario ou semanal."""
        if tipo == "semanal":
            resumo = self.model.get_resumo_semanal()
            titulo = "Relatorio Semanal"
        else:
            resumo = self.model.get_resumo_diario()
            titulo = "Relatorio Diario"

        custo = DPITheme.formatar_reais(resumo["custo_total_centavos"])
        self.view.mostrar_aviso(
            titulo,
            f"Periodo: {resumo.get('data', resumo.get('periodo_inicio', ''))}\n"
            f"Total de impressoes: {resumo['total_impressoes']}\n"
            f"Custo total: {custo}",
        )

    def executar(self):
        self.view.mainloop()
