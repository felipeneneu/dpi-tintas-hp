import json
import os
from datetime import datetime
from tkinter import filedialog, messagebox

from config.theme import DPITheme
from models.tinta_model import TintaModel
from views.main_view import MainView
from views.config_modal import ConfigModal


class MainController:
    """Controlador principal - conecta View e Model."""

    def __init__(self):
        self.model = TintaModel()
        self.view = MainView()

        self.view.set_callbacks(
            calcular=self._on_calcular,
            configurar=self._on_configurar,
            exportar=self._on_exportar,
        )
        self.view.set_reabastecer_callbacks(self._on_reabastecer)

        self._carregar_dados_iniciais()

    def _carregar_dados_iniciais(self):
        config = self.model.get_configuracoes()
        for cor, dados in config.items():
            self.view.set_nivel_atual(cor, dados["nivel_atual"])

        ultimo = self.model.get_ultimo_rodagem()
        if ultimo:
            niveis_fim = {
                "C": ultimo["c_fim"],
                "M": ultimo["m_fim"],
                "Y": ultimo["y_fim"],
                "K": ultimo["k_fim"],
            }
            self.view.set_niveis_finais(niveis_fim)
            self.view.set_resultado(ultimo["custo_total_centavos"])

    def _on_reabastecer(self, cor: str):
        self.model.reabastecer(cor)
        self.view.set_nivel_atual(cor, 100.0)
        self.view.mostrar_sucesso(
            f"Cartucho {DPITheme.CMYK[cor]['name']} reabastecido para 100%!"
        )

    def _on_calcular(self):
        niveis = self.view.get_niveis()

        niveis_ini = {}
        niveis_fim = {}
        for cor in ["C", "M", "Y", "K"]:
            ini, fim = niveis[cor]
            niveis_ini[cor] = ini
            niveis_fim[cor] = fim

        for cor in ["C", "M", "Y", "K"]:
            if niveis_fim[cor] > niveis_ini[cor]:
                self.view.mostrar_aviso(
                    "Erro",
                    f"O n\u00edvel final de {DPITheme.CMYK[cor]['name']} "
                    f"({niveis_fim[cor]:.1f}%) n\u00e3o pode ser maior "
                    f"que o inicial ({niveis_ini[cor]:.1f}%)!",
                )
                return

        detalhes, custo_total = self.model.calcular_custos(niveis_ini, niveis_fim)

        texto_detalhes = " | ".join(
            [
                f"{cor}: {d['gasto']:.1f}% = {DPITheme.formatar_reais(d['custo_centavos'])}"
                for cor, d in detalhes.items()
                if d["gasto"] > 0
            ]
        )
        if not texto_detalhes:
            texto_detalhes = "Sem consumo registrado"

        self.view.set_resultado(custo_total, texto_detalhes)

        self.model.salvar_rodagem(niveis_ini, niveis_fim, custo_total)

        for cor in ["C", "M", "Y", "K"]:
            self.view.set_nivel_atual(cor, niveis_fim[cor])

        proximos = {cor: niveis_fim[cor] for cor in ["C", "M", "Y", "K"]}
        self.view.set_niveis_finais(proximos)

        self.view.mostrar_sucesso(
            f"Rodagem registrada!\n\n"
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
            self.view.mostrar_sucesso("Configura\u00e7\u00e3o salva com sucesso!")

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

    def executar(self):
        self.view.mainloop()
