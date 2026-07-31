from models.database import Database


class TintaModel:
    CORES = ["C", "M", "Y", "K"]

    def __init__(self):
        self.db = Database.get_instance()

    def get_configuracoes(self) -> dict:
        """Retorna config de todas as cores."""
        config = {}
        for cor in self.CORES:
            dados = self.db.buscar_um(
                "SELECT * FROM configuracao WHERE cor = ?", (cor,)
            )
            if dados:
                config[cor] = {
                    "capacidade_ml": dados["capacidade_ml"],
                    "preco_centavos": dados["preco_cartucho_centavos"],
                    "nivel_atual": dados["nivel_atual_pct"],
                }
        return config

    def get_niveis_atuais(self) -> dict:
        """Retorna apenas o nivel atual de cada cor."""
        niveis = {}
        for cor in self.CORES:
            dados = self.db.buscar_um(
                "SELECT nivel_atual_pct FROM configuracao WHERE cor = ?", (cor,)
            )
            niveis[cor] = dados["nivel_atual_pct"] if dados else 100.0
        return niveis

    def get_preco_centavos(self, cor: str) -> int:
        """Retorna o preco do cartucho em centavos."""
        dados = self.db.buscar_um(
            "SELECT preco_cartucho_centavos FROM configuracao WHERE cor = ?",
            (cor,),
        )
        return dados["preco_cartucho_centavos"] if dados else 5000

    def reabastecer(self, cor: str):
        """Reseta o nivel da cor para 100%."""
        self.db.executar(
            "UPDATE configuracao SET nivel_atual_pct = 100.0 WHERE cor = ?", (cor,)
        )
        self.db.commitar()

    def atualizar_nivel(self, cor: str, nivel: float):
        """Atualiza o nivel da cor."""
        nivel = max(0.0, min(100.0, nivel))
        self.db.executar(
            "UPDATE configuracao SET nivel_atual_pct = ? WHERE cor = ?",
            (nivel, cor),
        )
        self.db.commitar()

    def atualizar_configuracao(
        self, cor: str, capacidade_ml: float, preco_centavos: int
    ):
        """Atualiza capacidade e preco do cartucho."""
        self.db.executar(
            """UPDATE configuracao
               SET capacidade_ml = ?, preco_cartucho_centavos = ?
               WHERE cor = ?""",
            (capacidade_ml, preco_centavos, cor),
        )
        self.db.commitar()

    def calcular_custos(
        self,
        niveis_ini: dict,
        niveis_fim: dict,
    ) -> tuple[dict, int]:
        """Calcula gasto e custo por cor.
        Retorna (detalhes_por_cor, custo_total_centavos).
        """
        config = self.get_configuracoes()
        detalhes = {}
        custo_total = 0

        for cor in self.CORES:
            ini = niveis_ini.get(cor, 0)
            fim = niveis_fim.get(cor, 0)
            gasto = max(0.0, ini - fim)

            preco = config[cor]["preco_centavos"]
            custo_centavos = round((gasto / 100) * preco)
            custo_total += custo_centavos

            detalhes[cor] = {
                "ini": ini,
                "fim": fim,
                "gasto": gasto,
                "custo_centavos": custo_centavos,
            }

        return detalhes, custo_total

    def salvar_rodagem(
        self,
        niveis_ini: dict,
        niveis_fim: dict,
        custo_total_centavos: int,
    ):
        """Salva rodagem e atualiza niveis atuais."""
        self.db.executar(
            """INSERT INTO rodagens
               (c_ini, m_ini, y_ini, k_ini, c_fim, m_fim, y_fim, k_fim, custo_total_centavos)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                niveis_ini.get("C", 0),
                niveis_ini.get("M", 0),
                niveis_ini.get("Y", 0),
                niveis_ini.get("K", 0),
                niveis_fim.get("C", 0),
                niveis_fim.get("M", 0),
                niveis_fim.get("Y", 0),
                niveis_fim.get("K", 0),
                custo_total_centavos,
            ),
        )

        for cor in self.CORES:
            fim = niveis_fim.get(cor, 0)
            self.db.executar(
                "UPDATE configuracao SET nivel_atual_pct = ? WHERE cor = ?",
                (fim, cor),
            )

        self.db.commitar()

    def get_historico(self, limite: int = 50) -> list:
        """Retorna historico de rodagens."""
        return self.db.buscar_todos(
            "SELECT * FROM rodagens ORDER BY data_hora DESC LIMIT ?", (limite,)
        )

    def get_ultimo_rodagem(self) -> dict | None:
        """Retorna a ultima rodagem registrada."""
        return self.db.buscar_um(
            "SELECT * FROM rodagens ORDER BY data_hora DESC LIMIT 1"
        )

    def exportar_json(self) -> dict:
        """Exporta todos os dados para dicionario."""
        config = self.get_configuracoes()
        historico = self.get_historico(limite=99999)
        return {
            "configuracoes": config,
            "historico": [
                {
                    "data_hora": r["data_hora"],
                    "c_ini": r["c_ini"],
                    "m_ini": r["m_ini"],
                    "y_ini": r["y_ini"],
                    "k_ini": r["k_ini"],
                    "c_fim": r["c_fim"],
                    "m_fim": r["m_fim"],
                    "y_fim": r["y_fim"],
                    "k_fim": r["k_fim"],
                    "custo_total_centavos": r["custo_total_centavos"],
                }
                for r in historico
            ],
        }

    def exportar_sql(self) -> str:
        """Gera script SQL com todos os dados."""
        linhas = [
            "-- DPI Tintas HP - Exportacao SQL",
            "-- Gerado automaticamente",
            "",
            "DELETE FROM configuracao;",
            "DELETE FROM rodagens;",
            "",
        ]

        config = self.get_configuracoes()
        for cor, dados in config.items():
            linhas.append(
                f"INSERT INTO configuracao (cor, capacidade_ml, preco_cartucho_centavos, nivel_atual_pct) "
                f"VALUES ('{cor}', {dados['capacidade_ml']}, {dados['preco_centavos']}, {dados['nivel_atual']:.1f});"
            )

        linhas.append("")

        historico = self.get_historico(limite=99999)
        for r in reversed(historico):
            linhas.append(
                f"INSERT INTO rodagens (data_hora, c_ini, m_ini, y_ini, k_ini, c_fim, m_fim, y_fim, k_fim, custo_total_centavos) "
                f"VALUES ('{r['data_hora']}', {r['c_ini']}, {r['m_ini']}, {r['y_ini']}, {r['k_ini']}, "
                f"{r['c_fim']}, {r['m_fim']}, {r['y_fim']}, {r['k_fim']}, {r['custo_total_centavos']});"
            )

        return "\n".join(linhas)
