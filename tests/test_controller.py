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

        niveis_ini = {"C": 775, "M": 775, "Y": 775, "K": 775, "LC": 775, "LM": 775, "OP": 775}
        niveis_fim = {"C": 620, "M": 697.5, "Y": 542.5, "K": 658.75, "LC": 775, "LM": 775, "OP": 775}

        detalhes, custo_total = model.calcular_custos(niveis_ini, niveis_fim)
        model.salvar_impressao(
            None, None, "teste.pdf", niveis_ini, niveis_fim, custo_total
        )

        config = model.get_configuracoes()
        assert config["C"]["nivel_atual_ml"] == 620.0
        assert config["M"]["nivel_atual_ml"] == 697.5
        assert config["Y"]["nivel_atual_ml"] == 542.5
        assert config["K"]["nivel_atual_ml"] == 658.75

        impressoes = model.get_impressoes()
        assert impressoes[0]["custo_total_centavos"] == 3750

    def test_fluxo_varias_impressoes_acumula(self, fresh_db):
        model = self._make_model(fresh_db)

        model.salvar_impressao(
            None, None, "arq1.pdf",
            {"C": 775, "M": 775, "Y": 775, "K": 775, "LC": 775, "LM": 775, "OP": 775},
            {"C": 620, "M": 697.5, "Y": 542.5, "K": 658.75, "LC": 775, "LM": 775, "OP": 775},
            3750,
        )

        model.salvar_impressao(
            None, None, "arq2.pdf",
            {"C": 620, "M": 697.5, "Y": 542.5, "K": 658.75, "LC": 775, "LM": 775, "OP": 775},
            {"C": 465, "M": 620, "Y": 387.5, "K": 542.5, "LC": 775, "LM": 775, "OP": 775},
            2500,
        )

        config = model.get_configuracoes()
        assert config["C"]["nivel_atual_ml"] == 465.0

        impressoes = model.get_impressoes()
        assert len(impressoes) == 2

    def test_fluxo_reabastecer_depois_de_impressao(self, fresh_db):
        model = self._make_model(fresh_db)

        model.salvar_impressao(
            None, None, "arq.pdf",
            {"C": 775, "M": 775, "Y": 775, "K": 775, "LC": 775, "LM": 775, "OP": 775},
            {"C": 620, "M": 697.5, "Y": 775, "K": 775, "LC": 775, "LM": 775, "OP": 775},
            1000,
        )

        model.reabastecer("C")

        config = model.get_configuracoes()
        assert config["C"]["nivel_atual_ml"] == 775.0
        assert config["M"]["nivel_atual_ml"] == 697.5

    def test_nivel_nao_pode_ser_maior_que_anterior(self, model):
        niveis_ini = {"C": 620, "M": 620, "Y": 620, "K": 620, "LC": 0, "LM": 0, "OP": 0}
        niveis_fim = {"C": 775, "M": 620, "Y": 620, "K": 620, "LC": 0, "LM": 0, "OP": 0}

        detalhes, custo_total = model.calcular_custos(niveis_ini, niveis_fim)

        # gasto = max(0, 620 - 775) = 0, custo = 0
        assert detalhes["C"]["gasto_ml"] == 0.0
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


class TestControllerPedidoBobina:
    """Testes de integracao para pedidos e bobinas."""

    def _make_model(self, fresh_db):
        m = TintaModel.__new__(TintaModel)
        m.db = fresh_db
        return m

    def test_fluxo_pedido_com_impressao(self, fresh_db):
        model = self._make_model(fresh_db)

        pedido_id = model.criar_pedido("PED-001", "Cliente ABC")

        model.salvar_impressao(
            pedido_id, None, "banner.pdf",
            {"C": 775, "M": 775, "Y": 775, "K": 775, "LC": 775, "LM": 775, "OP": 775},
            {"C": 620, "M": 775, "Y": 775, "K": 775, "LC": 775, "LM": 775, "OP": 775},
            1000,
        )

        resultados = model.buscar_impressoes("PED-001")
        assert len(resultados) == 1
        assert resultados[0]["pedido_numero"] == "PED-001"

    def test_fluxo_bobina_com_impressao(self, fresh_db):
        model = self._make_model(fresh_db)

        bobina_id = model.criar_bobina("60cm", "Vinil", "Brilho")

        model.salvar_impressao(
            None, bobina_id, "cartaz.pdf",
            {"C": 775, "M": 775, "Y": 775, "K": 775, "LC": 775, "LM": 775, "OP": 775},
            {"C": 620, "M": 775, "Y": 775, "K": 775, "LC": 775, "LM": 775, "OP": 775},
            1000,
        )

        impressoes = model.get_impressoes({"bobina_id": bobina_id})
        assert len(impressoes) == 1
        assert impressoes[0]["bobina_id"] == bobina_id

    def test_deletar_pedido_com_impressoes(self, fresh_db):
        model = self._make_model(fresh_db)

        pedido_id = model.criar_pedido("PED-002", "Teste Delete")
        model.salvar_impressao(
            pedido_id, None, "arq.pdf",
            {"C": 775, "M": 775, "Y": 775, "K": 775, "LC": 775, "LM": 775, "OP": 775},
            {"C": 620, "M": 775, "Y": 775, "K": 775, "LC": 775, "LM": 775, "OP": 775},
            1000,
        )

        model.deletar_pedido(pedido_id)
        pedidos = model.get_pedidos()
        assert len(pedidos) == 0

        # Impressao continua existindo (sem cascade)
        impressoes = model.get_impressoes()
        assert len(impressoes) == 1
