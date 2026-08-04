from config.theme import DPITheme


class TestFormatarReais:
    def test_zero(self):
        assert DPITheme.formatar_reais(0) == "R$ 0,00"

    def test_valores_inteiros(self):
        assert DPITheme.formatar_reais(1000) == "R$ 10,00"
        assert DPITheme.formatar_reais(5000) == "R$ 50,00"

    def test_centavos(self):
        assert DPITheme.formatar_reais(150) == "R$ 1,50"
        assert DPITheme.formatar_reais(1050) == "R$ 10,50"

    def test_grandes_valores(self):
        assert DPITheme.formatar_reais(123456) == "R$ 1234,56"


class TestParseReais:
    def test_parse_basico(self):
        assert DPITheme.parse_reais("R$ 10,00") == 1000

    def test_parse_com_casas_decimais(self):
        assert DPITheme.parse_reais("R$ 1,50") == 150

    def test_parse_só_numero(self):
        assert DPITheme.parse_reais("10,00") == 1000

    def test_parse_invalido(self):
        assert DPITheme.parse_reais("abc") == 0


class TestCores:
    def test_cores_tem_7_entradas(self):
        assert len(DPITheme.CORES) == 7

    def test_cores_contem_cmyk_lclm_op(self):
        esperadas = {"C", "M", "Y", "K", "LC", "LM", "OP"}
        assert set(DPITheme.CORES.keys()) == esperadas

    def test_cada_cor_tem_campos(self):
        for cor, dados in DPITheme.CORES.items():
            assert "name" in dados, f"Cor {cor} sem 'name'"
            assert "hex" in dados, f"Cor {cor} sem 'hex'"
            assert "text_color" in dados, f"Cor {cor} sem 'text_color'"

    def test_cores_cores_names(self):
        assert DPITheme.CORES["C"]["name"] == "Cyan"
        assert DPITheme.CORES["M"]["name"] == "Magenta"
        assert DPITheme.CORES["Y"]["name"] == "Yellow"
        assert DPITheme.CORES["K"]["name"] == "Black"
        assert DPITheme.CORES["LC"]["name"] == "Light Cyan"
        assert DPITheme.CORES["LM"]["name"] == "Light Magenta"
        assert DPITheme.CORES["OP"]["name"] == "Opaca"

    def test_cmyk_alias(self):
        assert DPITheme.CMYK is DPITheme.CORES
