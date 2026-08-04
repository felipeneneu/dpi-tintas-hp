from models.tinta_model import TintaModel


class TestGetConfiguracoes:
    def test_retorna_todas_as_cores(self, model):
        config = model.get_configuracoes()
        assert set(config.keys()) == {"C", "M", "Y", "K", "LC", "LM", "OP"}

    def test_estrutura_dados(self, model):
        config = model.get_configuracoes()
        for cor in ["C", "M", "Y", "K", "LC", "LM", "OP"]:
            assert "capacidade_ml" in config[cor]
            assert "preco_centavos" in config[cor]
            assert "nivel_atual_ml" in config[cor]

    def test_valores_padrao(self, model):
        config = model.get_configuracoes()
        for cor in ["C", "M", "Y", "K", "LC", "LM", "OP"]:
            assert config[cor]["capacidade_ml"] == 775.0
            assert config[cor]["preco_centavos"] == 5000
            assert config[cor]["nivel_atual_ml"] == 775.0


class TestGetNiveisAtuais:
    def test_retorna_niveis(self, model):
        niveis = model.get_niveis_atuais()
        assert set(niveis.keys()) == {"C", "M", "Y", "K", "LC", "LM", "OP"}

    def test_niveis_padrao(self, model):
        niveis = model.get_niveis_atuais()
        for cor in ["C", "M", "Y", "K", "LC", "LM", "OP"]:
            assert niveis[cor] == 775.0


class TestGetPrecoCentavos:
    def test_retorna_preco(self, model):
        assert model.get_preco_centavos("C") == 5000

    def test_cor_inexistente_retorna_default(self, model):
        assert model.get_preco_centavos("X") == 5000


class TestGetCapacidadeMl:
    def test_retorna_capacidade(self, model):
        assert model.get_capacidade_ml("C") == 775.0

    def test_cor_inexistente_retorna_default(self, model):
        assert model.get_capacidade_ml("X") == 775.0


class TestCalcularCustos:
    def test_calculo_basico(self, model):
        niveis_ini = {"C": 775, "M": 775, "Y": 775, "K": 775, "LC": 775, "LM": 775, "OP": 775}
        niveis_fim = {"C": 620, "M": 697.5, "Y": 542.5, "K": 658.75, "LC": 775, "LM": 775, "OP": 775}

        detalhes, custo_total = model.calcular_custos(niveis_ini, niveis_fim)

        # Cyan: gasto=155ml, capacidade=775, preco=5000 -> custo = (155/775)*5000 = 1000
        assert detalhes["C"]["gasto_ml"] == 155.0
        assert detalhes["C"]["custo_centavos"] == 1000

        # Magenta: gasto=77.5ml -> custo = (77.5/775)*5000 = 500
        assert detalhes["M"]["gasto_ml"] == 77.5
        assert detalhes["M"]["custo_centavos"] == 500

        # Yellow: gasto=232.5ml -> custo = (232.5/775)*5000 = 1500
        assert detalhes["Y"]["gasto_ml"] == 232.5
        assert detalhes["Y"]["custo_centavos"] == 1500

        # Black: gasto=116.25ml -> custo = (116.25/775)*5000 = 750
        assert detalhes["K"]["gasto_ml"] == 116.25
        assert detalhes["K"]["custo_centavos"] == 750

        # Total = 1000 + 500 + 1500 + 750 = 3750
        assert custo_total == 3750

    def test_sem_gasto(self, model):
        niveis_ini = {"C": 775, "M": 775, "Y": 775, "K": 775, "LC": 775, "LM": 775, "OP": 775}
        niveis_fim = {"C": 775, "M": 775, "Y": 775, "K": 775, "LC": 775, "LM": 775, "OP": 775}

        detalhes, custo_total = model.calcular_custos(niveis_ini, niveis_fim)

        for cor in ["C", "M", "Y", "K", "LC", "LM", "OP"]:
            assert detalhes[cor]["gasto_ml"] == 0.0
            assert detalhes[cor]["custo_centavos"] == 0
        assert custo_total == 0

    def test_gasto_total_capacidade_inteira(self, model):
        niveis_ini = {"C": 775, "M": 0, "Y": 0, "K": 0, "LC": 0, "LM": 0, "OP": 0}
        niveis_fim = {"C": 0, "M": 0, "Y": 0, "K": 0, "LC": 0, "LM": 0, "OP": 0}

        detalhes, custo_total = model.calcular_custos(niveis_ini, niveis_fim)

        assert detalhes["C"]["gasto_ml"] == 775.0
        assert detalhes["C"]["custo_centavos"] == 5000
        assert custo_total == 5000

    def test_valores_finais_maiores_sao_tratados(self, model):
        niveis_ini = {"C": 387.5, "M": 387.5, "Y": 387.5, "K": 387.5, "LC": 0, "LM": 0, "OP": 0}
        niveis_fim = {"C": 465, "M": 387.5, "Y": 387.5, "K": 387.5, "LC": 0, "LM": 0, "OP": 0}

        detalhes, custo_total = model.calcular_custos(niveis_ini, niveis_fim)

        # gasto = max(0, 387.5 - 465) = 0 (tratado como zero)
        assert detalhes["C"]["gasto_ml"] == 0.0
        assert detalhes["C"]["custo_centavos"] == 0

    def test_preco_diferente_por_cor(self, model):
        model.atualizar_configuracao("C", 200.0, 10000)

        niveis_ini = {"C": 200, "M": 775, "Y": 0, "K": 0, "LC": 0, "LM": 0, "OP": 0}
        niveis_fim = {"C": 160, "M": 620, "Y": 0, "K": 0, "LC": 0, "LM": 0, "OP": 0}

        detalhes, custo_total = model.calcular_custos(niveis_ini, niveis_fim)

        assert detalhes["C"]["custo_centavos"] == 2000  # (40/200)*10000
        assert detalhes["M"]["custo_centavos"] == 1000  # (155/775)*5000


class TestSalvarImpressao:
    def test_insere_impressao_e_atualiza_nivel(self, model):
        niveis_ini = {"C": 775, "M": 775, "Y": 775, "K": 775, "LC": 775, "LM": 775, "OP": 775}
        niveis_fim = {"C": 620, "M": 697.5, "Y": 542.5, "K": 658.75, "LC": 775, "LM": 775, "OP": 775}

        impressao_id = model.salvar_impressao(
            pedido_id=None,
            bobina_id=None,
            nome_arquivo="teste.pdf",
            niveis_ini_ml=niveis_ini,
            niveis_fim_ml=niveis_fim,
            custo_total_centavos=3750,
        )

        assert impressao_id is not None

        # Verifica INSERT na tabela impressoes
        impressao = model.db.buscar_um(
            "SELECT * FROM impressoes WHERE id = ?", (impressao_id,)
        )
        assert impressao is not None
        assert impressao["nome_arquivo"] == "teste.pdf"
        assert impressao["c_ini_ml"] == 775
        assert impressao["c_fim_ml"] == 620
        assert impressao["custo_total_centavos"] == 3750

        # Verifica UPDATE em configuracao
        config = model.get_configuracoes()
        assert config["C"]["nivel_atual_ml"] == 620.0
        assert config["M"]["nivel_atual_ml"] == 697.5
        assert config["Y"]["nivel_atual_ml"] == 542.5
        assert config["K"]["nivel_atual_ml"] == 658.75

    def test_multiplos_impressoes(self, model):
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
        assert config["M"]["nivel_atual_ml"] == 620.0
        assert config["Y"]["nivel_atual_ml"] == 387.5
        assert config["K"]["nivel_atual_ml"] == 542.5

        impressoes = model.get_impressoes()
        assert len(impressoes) == 2


class TestFinalizarImpressao:
    def test_finaliza_impressao(self, model):
        niveis_ini = {"C": 775, "M": 775, "Y": 775, "K": 775, "LC": 775, "LM": 775, "OP": 775}

        impressao_id = model.salvar_impressao(
            None, None, "incompleto.pdf",
            niveis_ini,
            niveis_ini,
            0,
        )

        model.finalizar_impressao(
            impressao_id,
            niveis_fim_ml={"C": 620, "M": 775, "Y": 775, "K": 775, "LC": 775, "LM": 775, "OP": 775},
            custo_total_centavos=1000,
        )

        impressao = model.db.buscar_um(
            "SELECT * FROM impressoes WHERE id = ?", (impressao_id,)
        )
        assert impressao["custo_total_centavos"] == 1000
        assert impressao["c_fim_ml"] == 620

        config = model.get_configuracoes()
        assert config["C"]["nivel_atual_ml"] == 620.0


class TestSalvarRodagem:
    def test_insere_rodagem_e_atualiza_nivel(self, model):
        niveis_ini = {"C": 100, "M": 100, "Y": 100, "K": 100}
        niveis_fim = {"C": 80, "M": 90, "Y": 70, "K": 85}

        model.salvar_rodagem(niveis_ini, niveis_fim, 3750)

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

        config = model.get_configuracoes()
        assert config["C"]["nivel_atual_ml"] == (80 / 100.0) * 775.0
        assert config["M"]["nivel_atual_ml"] == (90 / 100.0) * 775.0
        assert config["Y"]["nivel_atual_ml"] == (70 / 100.0) * 775.0
        assert config["K"]["nivel_atual_ml"] == (85 / 100.0) * 775.0

    def test_multiplos_rodagens(self, model):
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

        config = model.get_configuracoes()
        assert config["C"]["nivel_atual_ml"] == (60 / 100.0) * 775.0
        assert config["M"]["nivel_atual_ml"] == (80 / 100.0) * 775.0
        assert config["Y"]["nivel_atual_ml"] == (50 / 100.0) * 775.0
        assert config["K"]["nivel_atual_ml"] == (70 / 100.0) * 775.0

        historico = model.get_historico()
        assert len(historico) == 2


class TestReabastecer:
    def test_reabastecer_cor(self, model):
        model.atualizar_nivel("C", 400.0)
        model.reabastecer("C")

        config = model.get_configuracoes()
        assert config["C"]["nivel_atual_ml"] == 775.0

    def test_reabastecer_nao_afeta_outras_cores(self, model):
        model.atualizar_nivel("C", 400.0)
        model.atualizar_nivel("M", 300.0)
        model.reabastecer("C")

        config = model.get_configuracoes()
        assert config["C"]["nivel_atual_ml"] == 775.0
        assert config["M"]["nivel_atual_ml"] == 300.0


class TestAtualizarNivel:
    def test_atualiza_nivel(self, model):
        model.atualizar_nivel("C", 500.5)
        config = model.get_configuracoes()
        assert config["C"]["nivel_atual_ml"] == 500.5

    def test_nivel_limitado_a_capacidade(self, model):
        model.atualizar_nivel("C", 1500.0)
        config = model.get_configuracoes()
        assert config["C"]["nivel_atual_ml"] == 775.0

    def test_nivel_limitado_a_0(self, model):
        model.atualizar_nivel("C", -10.0)
        config = model.get_configuracoes()
        assert config["C"]["nivel_atual_ml"] == 0.0


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


class TestPedidos:
    def test_criar_pedido(self, model):
        pedido_id = model.criar_pedido("PED-001", "Cliente ABC")
        assert pedido_id is not None

        pedidos = model.get_pedidos()
        assert len(pedidos) == 1
        assert pedidos[0]["numero"] == "PED-001"
        assert pedidos[0]["nome"] == "Cliente ABC"

    def test_deletar_pedido(self, model):
        pedido_id = model.criar_pedido("PED-002", "Cliente XYZ")
        model.deletar_pedido(pedido_id)

        pedidos = model.get_pedidos()
        assert len(pedidos) == 0

    def test_multiplos_pedidos(self, model):
        model.criar_pedido("PED-001", "A")
        model.criar_pedido("PED-002", "B")
        model.criar_pedido("PED-003", "C")

        pedidos = model.get_pedidos()
        assert len(pedidos) == 3


class TestBobinas:
    def test_criar_bobina(self, model):
        bobina_id = model.criar_bobina("60cm", "Vinil", "Brilho")
        assert bobina_id is not None

        bobinas = model.get_bobinas()
        assert len(bobinas) == 1
        assert bobinas[0]["tamanho"] == "60cm"
        assert bobinas[0]["material"] == "Vinil"
        assert bobinas[0]["tipo"] == "Brilho"

    def test_atualizar_bobina(self, model):
        bobina_id = model.criar_bobina("60cm", "Vinil", "Brilho")
        model.atualizar_bobina(bobina_id, "90cm", "Lona", "Fosco")

        bobinas = model.get_bobinas()
        assert bobinas[0]["tamanho"] == "90cm"
        assert bobinas[0]["material"] == "Lona"
        assert bobinas[0]["tipo"] == "Fosco"

    def test_deletar_bobina(self, model):
        bobina_id = model.criar_bobina("60cm", "Vinil", "Brilho")
        model.deletar_bobina(bobina_id)

        bobinas = model.get_bobinas()
        assert len(bobinas) == 0

    def test_multiplos_bobinas(self, model):
        model.criar_bobina("60cm", "Vinil", "Brilho")
        model.criar_bobina("90cm", "Lona", "Fosco")

        bobinas = model.get_bobinas()
        assert len(bobinas) == 2


class TestGetImpressoes:
    def test_impressoes_vazio(self, model):
        impressoes = model.get_impressoes()
        assert len(impressoes) == 0

    def test_impressoes_com_dados(self, model):
        model.salvar_impressao(
            None, None, "arquivo.pdf",
            {"C": 775, "M": 775, "Y": 775, "K": 775, "LC": 775, "LM": 775, "OP": 775},
            {"C": 620, "M": 775, "Y": 775, "K": 775, "LC": 775, "LM": 775, "OP": 775},
            1000,
        )

        impressoes = model.get_impressoes()
        assert len(impressoes) == 1

    def test_filtrar_por_pedido(self, model):
        pedido_id = model.criar_pedido("PED-001", "Teste")
        model.salvar_impressao(
            pedido_id, None, "arq1.pdf",
            {"C": 775, "M": 775, "Y": 775, "K": 775, "LC": 775, "LM": 775, "OP": 775},
            {"C": 620, "M": 775, "Y": 775, "K": 775, "LC": 775, "LM": 775, "OP": 775},
            1000,
        )
        model.salvar_impressao(
            None, None, "arq2.pdf",
            {"C": 775, "M": 775, "Y": 775, "K": 775, "LC": 775, "LM": 775, "OP": 775},
            {"C": 620, "M": 775, "Y": 775, "K": 775, "LC": 775, "LM": 775, "OP": 775},
            1000,
        )

        impressoes = model.get_impressoes({"pedido_id": pedido_id})
        assert len(impressoes) == 1
        assert impressoes[0]["pedido_id"] == pedido_id


class TestBuscarImpressoes:
    def test_busca_por_nome_arquivo(self, model):
        model.salvar_impressao(
            None, None, "banner_final.pdf",
            {"C": 775, "M": 775, "Y": 775, "K": 775, "LC": 775, "LM": 775, "OP": 775},
            {"C": 620, "M": 775, "Y": 775, "K": 775, "LC": 775, "LM": 775, "OP": 775},
            1000,
        )

        resultados = model.buscar_impressoes("banner")
        assert len(resultados) == 1

    def test_busca_nao_encontra(self, model):
        model.salvar_impressao(
            None, None, "arquivo.pdf",
            {"C": 775, "M": 775, "Y": 775, "K": 775, "LC": 775, "LM": 775, "OP": 775},
            {"C": 620, "M": 775, "Y": 775, "K": 775, "LC": 775, "LM": 775, "OP": 775},
            1000,
        )

        resultados = model.buscar_impressoes("xyz")
        assert len(resultados) == 0

    def test_busca_por_pedido(self, model):
        pedido_id = model.criar_pedido("PED-999", "Busca Teste")
        model.salvar_impressao(
            pedido_id, None, "arquivo.pdf",
            {"C": 775, "M": 775, "Y": 775, "K": 775, "LC": 775, "LM": 775, "OP": 775},
            {"C": 620, "M": 775, "Y": 775, "K": 775, "LC": 775, "LM": 775, "OP": 775},
            1000,
        )

        resultados = model.buscar_impressoes("PED-999")
        assert len(resultados) == 1


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
        assert "impressoes" in dados
        assert len(dados["historico"]) == 1


class TestExportarSql:
    def test_exportar_sql(self, model):
        sql = model.exportar_sql()
        assert "INSERT INTO configuracao" in sql
        assert "DELETE FROM configuracao" in sql
