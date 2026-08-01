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
