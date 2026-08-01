from models.tinta_model import TintaModel


class TestGetConfiguracoes:
    def test_retorna_todas_as_cores(self, model):
        config = model.get_configuracoes()
        assert set(config.keys()) == {"C", "M", "Y", "K"}

    def test_estrutura_dados(self, model):
        config = model.get_configuracoes()
        for cor in ["C", "M", "Y", "K"]:
            assert "capacidade_ml" in config[cor]
            assert "preco_centavos" in config[cor]
            assert "nivel_atual" in config[cor]

    def test_valores_padrao(self, model):
        config = model.get_configuracoes()
        for cor in ["C", "M", "Y", "K"]:
            assert config[cor]["capacidade_ml"] == 100.0
            assert config[cor]["preco_centavos"] == 5000
            assert config[cor]["nivel_atual"] == 100.0


class TestGetNiveisAtuais:
    def test_retorna_niveis(self, model):
        niveis = model.get_niveis_atuais()
        assert set(niveis.keys()) == {"C", "M", "Y", "K"}

    def test_niveis_padrao(self, model):
        niveis = model.get_niveis_atuais()
        for cor in ["C", "M", "Y", "K"]:
            assert niveis[cor] == 100.0


class TestGetPrecoCentavos:
    def test_retorna_preco(self, model):
        assert model.get_preco_centavos("C") == 5000

    def test_cor_inexistente_retorna_default(self, model):
        assert model.get_preco_centavos("X") == 5000


class TestCalcularCustos:
    def test_calculo_basico(self, model):
        niveis_ini = {"C": 100, "M": 100, "Y": 100, "K": 100}
        niveis_fim = {"C": 80, "M": 90, "Y": 70, "K": 85}

        detalhes, custo_total = model.calcular_custos(niveis_ini, niveis_fim)

        # Cyan: gasto=20%, preco=5000 -> custo = (20/100)*5000 = 1000
        assert detalhes["C"]["gasto"] == 20.0
        assert detalhes["C"]["custo_centavos"] == 1000

        # Magenta: gasto=10%, preco=5000 -> custo = (10/100)*5000 = 500
        assert detalhes["M"]["gasto"] == 10.0
        assert detalhes["M"]["custo_centavos"] == 500

        # Yellow: gasto=30%, preco=5000 -> custo = (30/100)*5000 = 1500
        assert detalhes["Y"]["gasto"] == 30.0
        assert detalhes["Y"]["custo_centavos"] == 1500

        # Black: gasto=15%, preco=5000 -> custo = (15/100)*5000 = 750
        assert detalhes["K"]["gasto"] == 15.0
        assert detalhes["K"]["custo_centavos"] == 750

        # Total = 1000 + 500 + 1500 + 750 = 3750
        assert custo_total == 3750

    def test_sem_gasto(self, model):
        niveis_ini = {"C": 100, "M": 100, "Y": 100, "K": 100}
        niveis_fim = {"C": 100, "M": 100, "Y": 100, "K": 100}

        detalhes, custo_total = model.calcular_custos(niveis_ini, niveis_fim)

        for cor in ["C", "M", "Y", "K"]:
            assert detalhes[cor]["gasto"] == 0.0
            assert detalhes[cor]["custo_centavos"] == 0
        assert custo_total == 0

    def test_gasto_total_100_percent(self, model):
        niveis_ini = {"C": 100, "M": 0, "Y": 0, "K": 0}
        niveis_fim = {"C": 0, "M": 0, "Y": 0, "K": 0}

        detalhes, custo_total = model.calcular_custos(niveis_ini, niveis_fim)

        assert detalhes["C"]["gasto"] == 100.0
        assert detalhes["C"]["custo_centavos"] == 5000
        assert custo_total == 5000

    def test_valores_finais_maiores_sao_tratados(self, model):
        niveis_ini = {"C": 50, "M": 50, "Y": 50, "K": 50}
        niveis_fim = {"C": 60, "M": 50, "Y": 50, "K": 50}

        detalhes, custo_total = model.calcular_custos(niveis_ini, niveis_fim)

        # gasto = max(0, 50 - 60) = 0 (tratado como zero)
        assert detalhes["C"]["gasto"] == 0.0
        assert detalhes["C"]["custo_centavos"] == 0

    def test_preco_diferente_por_cor(self, model):
        model.atualizar_configuracao("C", 100.0, 10000)
        model.atualizar_configuracao("M", 100.0, 5000)

        niveis_ini = {"C": 100, "M": 100, "Y": 0, "K": 0}
        niveis_fim = {"C": 80, "M": 80, "Y": 0, "K": 0}

        detalhes, custo_total = model.calcular_custos(niveis_ini, niveis_fim)

        assert detalhes["C"]["custo_centavos"] == 2000  # (20/100)*10000
        assert detalhes["M"]["custo_centavos"] == 1000  # (20/100)*5000


class TestSalvarRodagem:
    def test_insere_rodagem_e_atualiza_nivel(self, model):
        niveis_ini = {"C": 100, "M": 100, "Y": 100, "K": 100}
        niveis_fim = {"C": 80, "M": 90, "Y": 70, "K": 85}

        model.salvar_rodagem(niveis_ini, niveis_fim, 3750)

        # Verifica INSERT na tabela rodagens
        rodagem = model.db.buscar_um(
            "SELECT * FROM rodagens ORDER BY id DESC LIMIT 1"
        )
        assert rodagem is not None
        assert rodagem["c_ini"] == 100
        assert rodagem["m_ini"] == 100
        assert rodagem["y_ini"] == 100
        assert rodagem["k_ini"] == 100
        assert rodagem["c_fim"] == 80
        assert rodagem["m_fim"] == 90
        assert rodagem["y_fim"] == 70
        assert rodagem["k_fim"] == 85
        assert rodagem["custo_total_centavos"] == 3750

        # Verifica UPDATE em configuracao
        config = model.get_configuracoes()
        assert config["C"]["nivel_atual"] == 80.0
        assert config["M"]["nivel_atual"] == 90.0
        assert config["Y"]["nivel_atual"] == 70.0
        assert config["K"]["nivel_atual"] == 85.0

    def test_multiplos_rodagens(self, model):
        # Primeira rodagem: 100 -> 80
        model.salvar_rodagem(
            {"C": 100, "M": 100, "Y": 100, "K": 100},
            {"C": 80, "M": 90, "Y": 70, "K": 85},
            3750,
        )

        # Segunda rodagem: 80 -> 60
        model.salvar_rodagem(
            {"C": 80, "M": 90, "Y": 70, "K": 85},
            {"C": 60, "M": 80, "Y": 50, "K": 70},
            2500,
        )

        config = model.get_configuracoes()
        assert config["C"]["nivel_atual"] == 60.0
        assert config["M"]["nivel_atual"] == 80.0
        assert config["Y"]["nivel_atual"] == 50.0
        assert config["K"]["nivel_atual"] == 70.0

        historico = model.get_historico()
        assert len(historico) == 2


class TestReabastecer:
    def test_reabastecer_cor(self, model):
        model.atualizar_nivel("C", 50.0)
        model.reabastecer("C")

        config = model.get_configuracoes()
        assert config["C"]["nivel_atual"] == 100.0

    def test_reabastecer_nao_afeta_outras_cores(self, model):
        model.atualizar_nivel("C", 50.0)
        model.atualizar_nivel("M", 30.0)
        model.reabastecer("C")

        config = model.get_configuracoes()
        assert config["C"]["nivel_atual"] == 100.0
        assert config["M"]["nivel_atual"] == 30.0


class TestAtualizarNivel:
    def test_atualiza_nivel(self, model):
        model.atualizar_nivel("C", 75.5)
        config = model.get_configuracoes()
        assert config["C"]["nivel_atual"] == 75.5

    def test_nivel_limitado_a_100(self, model):
        model.atualizar_nivel("C", 150.0)
        config = model.get_configuracoes()
        assert config["C"]["nivel_atual"] == 100.0

    def test_nivel_limitado_a_0(self, model):
        model.atualizar_nivel("C", -10.0)
        config = model.get_configuracoes()
        assert config["C"]["nivel_atual"] == 0.0


class TestAtualizarConfiguracao:
    def test_atualiza_capacidade_e_preco(self, model):
        model.atualizar_configuracao("C", 200.0, 8000)
        config = model.get_configuracoes()
        assert config["C"]["capacidade_ml"] == 200.0
        assert config["C"]["preco_centavos"] == 8000


class TestGetHistorico:
    def test_historico_vazio(self, model):
        historico = model.get_historico()
        assert len(historico) == 0

    def test_historico_com_registros(self, model):
        model.salvar_rodagem(
            {"C": 100, "M": 100, "Y": 100, "K": 100},
            {"C": 80, "M": 90, "Y": 70, "K": 85},
            3750,
        )
        model.salvar_rodagem(
            {"C": 80, "M": 90, "Y": 70, "K": 85},
            {"C": 60, "M": 80, "Y": 50, "K": 70},
            2500,
        )

        historico = model.get_historico(limite=1)
        assert len(historico) == 1


class TestGetUltimoRodagem:
    def test_ultimo_rodagem_vazio(self, model):
        assert model.get_ultimo_rodagem() is None

    def test_ultimo_rodagem(self, model):
        model.salvar_rodagem(
            {"C": 100, "M": 100, "Y": 100, "K": 100},
            {"C": 80, "M": 90, "Y": 70, "K": 85},
            3750,
        )

        ultimo = model.get_ultimo_rodagem()
        assert ultimo is not None
        assert ultimo["c_fim"] == 80


class TestExportarJson:
    def test_exportar_json(self, model):
        model.salvar_rodagem(
            {"C": 100, "M": 100, "Y": 100, "K": 100},
            {"C": 80, "M": 90, "Y": 70, "K": 85},
            3750,
        )

        dados = model.exportar_json()
        assert "configuracoes" in dados
        assert "historico" in dados
        assert len(dados["historico"]) == 1


class TestExportarSql:
    def test_exportar_sql(self, model):
        sql = model.exportar_sql()
        assert "INSERT INTO configuracao" in sql
        assert "DELETE FROM configuracao" in sql
