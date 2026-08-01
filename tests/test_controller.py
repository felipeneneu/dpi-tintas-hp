from unittest.mock import patch, MagicMock
from models.tinta_model import TintaModel


class TestControllerFluxoCalcular:
    """Testes de integracao do fluxo calcular + registrar."""

    def _make_model(self, fresh_db):
        m = TintaModel.__new__(TintaModel)
        m.db = fresh_db
        return m

    def test_fluxo_completo_calcula_e_salva(self, fresh_db):
        model = self._make_model(fresh_db)

        niveis_ini = {"C": 100, "M": 100, "Y": 100, "K": 100}
        niveis_fim = {"C": 80, "M": 90, "Y": 70, "K": 85}

        detalhes, custo_total = model.calcular_custos(niveis_ini, niveis_fim)
        model.salvar_rodagem(niveis_ini, niveis_fim, custo_total)

        config = model.get_configuracoes()
        assert config["C"]["nivel_atual"] == 80.0
        assert config["M"]["nivel_atual"] == 90.0
        assert config["Y"]["nivel_atual"] == 70.0
        assert config["K"]["nivel_atual"] == 85.0

        rodagem = model.get_ultimo_rodagem()
        assert rodagem["custo_total_centavos"] == 3750

    def test_fluxo_varias_rodagens_acumula(self, fresh_db):
        model = self._make_model(fresh_db)

        # Rodagem 1: 100 -> 80
        model.salvar_rodagem(
            {"C": 100, "M": 100, "Y": 100, "K": 100},
            {"C": 80, "M": 90, "Y": 70, "K": 85},
            3750,
        )

        # Rodagem 2: 80 -> 60
        model.salvar_rodagem(
            {"C": 80, "M": 90, "Y": 70, "K": 85},
            {"C": 60, "M": 80, "Y": 50, "K": 70},
            2500,
        )

        config = model.get_configuracoes()
        assert config["C"]["nivel_atual"] == 60.0

        historico = model.get_historico()
        assert len(historico) == 2

    def test_fluxo_reabastecer_depois_de_rodagem(self, fresh_db):
        model = self._make_model(fresh_db)

        model.salvar_rodagem(
            {"C": 100, "M": 100, "Y": 100, "K": 100},
            {"C": 80, "M": 90, "Y": 70, "K": 85},
            3750,
        )

        model.reabastecer("C")

        config = model.get_configuracoes()
        assert config["C"]["nivel_atual"] == 100.0
        assert config["M"]["nivel_atual"] == 90.0

    def test_nivel_nao_pode_ser_maior_que_anterior(self, model):
        niveis_ini = {"C": 80, "M": 80, "Y": 80, "K": 80}
        niveis_fim = {"C": 90, "M": 80, "Y": 80, "K": 80}

        detalhes, custo_total = model.calcular_custos(niveis_ini, niveis_fim)

        # gasto = max(0, 80 - 90) = 0, custo = 0
        assert detalhes["C"]["gasto"] == 0.0
        assert detalhes["C"]["custo_centavos"] == 0

    def test_exportar_importar_dados(self, fresh_db):
        model = self._make_model(fresh_db)

        model.atualizar_configuracao("C", 200.0, 8000)
        model.salvar_rodagem(
            {"C": 100, "M": 100, "Y": 100, "K": 100},
            {"C": 80, "M": 90, "Y": 70, "K": 85},
            3750,
        )

        dados = model.exportar_json()
        assert dados["configuracoes"]["C"]["capacidade_ml"] == 200.0
        assert dados["configuracoes"]["C"]["preco_centavos"] == 8000
        assert len(dados["historico"]) == 1

        sql = model.exportar_sql()
        assert "200.0" in sql
        assert "8000" in sql
