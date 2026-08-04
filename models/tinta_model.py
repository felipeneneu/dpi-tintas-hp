from models.database import Database


class TintaModel:
    CORES = ["C", "M", "Y", "K", "LC", "LM", "OP"]

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
                    "nivel_atual_ml": dados["nivel_atual_ml"],
                }
        return config

    def get_niveis_atuais(self) -> dict:
        """Retorna apenas o nivel atual de cada cor em ml."""
        niveis = {}
        for cor in self.CORES:
            dados = self.db.buscar_um(
                "SELECT nivel_atual_ml, capacidade_ml FROM configuracao WHERE cor = ?",
                (cor,),
            )
            if dados:
                niveis[cor] = dados["nivel_atual_ml"]
            else:
                config = self.get_configuracoes().get(cor, {})
                niveis[cor] = config.get("capacidade_ml", 775.0)
        return niveis

    def get_preco_centavos(self, cor: str) -> int:
        """Retorna o preco do cartucho em centavos."""
        dados = self.db.buscar_um(
            "SELECT preco_cartucho_centavos FROM configuracao WHERE cor = ?",
            (cor,),
        )
        return dados["preco_cartucho_centavos"] if dados else 5000

    def get_capacidade_ml(self, cor: str) -> float:
        """Retorna a capacidade do cartucho em ml."""
        dados = self.db.buscar_um(
            "SELECT capacidade_ml FROM configuracao WHERE cor = ?", (cor,)
        )
        return dados["capacidade_ml"] if dados else 775.0

    def reabastecer(self, cor: str):
        """Reseta o nivel da cor para capacidade maxima."""
        capacidade = self.get_capacidade_ml(cor)
        self.db.executar(
            "UPDATE configuracao SET nivel_atual_ml = ? WHERE cor = ?",
            (capacidade, cor),
        )
        self.db.commitar()

    def atualizar_nivel(self, cor: str, nivel_ml: float):
        """Atualiza o nivel da cor em ml."""
        capacidade = self.get_capacidade_ml(cor)
        nivel_ml = max(0.0, min(capacidade, nivel_ml))
        self.db.executar(
            "UPDATE configuracao SET nivel_atual_ml = ? WHERE cor = ?",
            (nivel_ml, cor),
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
        niveis_ini_ml: dict,
        niveis_fim_ml: dict,
    ) -> tuple[dict, int]:
        """Calcula gasto e custo por cor usando ml.
        Retorna (detalhes_por_cor, custo_total_centavos).
        """
        config = self.get_configuracoes()
        detalhes = {}
        custo_total = 0

        for cor in self.CORES:
            ini = niveis_ini_ml.get(cor, 0)
            fim = niveis_fim_ml.get(cor, 0)
            gasto_ml = max(0.0, ini - fim)
            capacidade = config[cor]["capacidade_ml"]
            preco = config[cor]["preco_centavos"]
            custo_centavos = round((gasto_ml / capacidade) * preco)
            custo_total += custo_centavos

            detalhes[cor] = {
                "ini_ml": ini,
                "fim_ml": fim,
                "gasto_ml": gasto_ml,
                "custo_centavos": custo_centavos,
            }

        return detalhes, custo_total

    def salvar_impressao(
        self,
        pedido_id: int | None,
        bobina_id: int | None,
        nome_arquivo: str,
        niveis_ini_ml: dict,
        niveis_fim_ml: dict,
        custo_total_centavos: int,
        data_inicio: str | None = None,
        data_fim: str | None = None,
        duracao_segundos: int | None = None,
    ) -> int:
        """Salva uma impressao e atualiza niveis atuais. Retorna o id."""
        from datetime import datetime

        if data_inicio is None:
            data_inicio = datetime.now().isoformat()
        if data_fim is None:
            data_fim = datetime.now().isoformat()

        cursor = self.db.executar(
            """INSERT INTO impressoes
               (pedido_id, bobina_id, nome_arquivo, data_inicio, data_fim,
                duracao_segundos,
                c_ini_ml, m_ini_ml, y_ini_ml, k_ini_ml, lc_ini_ml, lm_ini_ml, op_ini_ml,
                c_fim_ml, m_fim_ml, y_fim_ml, k_fim_ml, lc_fim_ml, lm_fim_ml, op_fim_ml,
                custo_total_centavos)
               VALUES (?, ?, ?, ?, ?, ?,
                       ?, ?, ?, ?, ?, ?, ?,
                       ?, ?, ?, ?, ?, ?, ?,
                       ?)""",
            (
                pedido_id,
                bobina_id,
                nome_arquivo,
                data_inicio,
                data_fim,
                duracao_segundos,
                niveis_ini_ml.get("C", 0),
                niveis_ini_ml.get("M", 0),
                niveis_ini_ml.get("Y", 0),
                niveis_ini_ml.get("K", 0),
                niveis_ini_ml.get("LC", 0),
                niveis_ini_ml.get("LM", 0),
                niveis_ini_ml.get("OP", 0),
                niveis_fim_ml.get("C", 0),
                niveis_fim_ml.get("M", 0),
                niveis_fim_ml.get("Y", 0),
                niveis_fim_ml.get("K", 0),
                niveis_fim_ml.get("LC", 0),
                niveis_fim_ml.get("LM", 0),
                niveis_fim_ml.get("OP", 0),
                custo_total_centavos,
            ),
        )

        for cor in self.CORES:
            fim = niveis_fim_ml.get(cor, 0)
            self.db.executar(
                "UPDATE configuracao SET nivel_atual_ml = ? WHERE cor = ?",
                (fim, cor),
            )

        self.db.commitar()
        return cursor.lastrowid

    def finalizar_impressao(
        self,
        impressao_id: int,
        niveis_fim_ml: dict,
        custo_total_centavos: int,
    ):
        """Finaliza uma impressao com niveis finais e custo."""
        from datetime import datetime

        self.db.executar(
            """UPDATE impressoes
               SET data_fim = ?, custo_total_centavos = ?,
                   c_fim_ml = ?, m_fim_ml = ?, y_fim_ml = ?, k_fim_ml = ?,
                   lc_fim_ml = ?, lm_fim_ml = ?, op_fim_ml = ?
               WHERE id = ?""",
            (
                datetime.now().isoformat(),
                custo_total_centavos,
                niveis_fim_ml.get("C", 0),
                niveis_fim_ml.get("M", 0),
                niveis_fim_ml.get("Y", 0),
                niveis_fim_ml.get("K", 0),
                niveis_fim_ml.get("LC", 0),
                niveis_fim_ml.get("LM", 0),
                niveis_fim_ml.get("OP", 0),
                impressao_id,
            ),
        )

        for cor in self.CORES:
            fim = niveis_fim_ml.get(cor, 0)
            self.db.executar(
                "UPDATE configuracao SET nivel_atual_ml = ? WHERE cor = ?",
                (fim, cor),
            )

        self.db.commitar()

    def get_impressoes(self, filtros: dict = None) -> list:
        """Retorna impressoes com filtros opcionais."""
        sql = "SELECT * FROM impressoes"
        params = []
        condicoes = []

        if filtros:
            if "pedido_id" in filtros:
                condicoes.append("pedido_id = ?")
                params.append(filtros["pedido_id"])
            if "bobina_id" in filtros:
                condicoes.append("bobina_id = ?")
                params.append(filtros["bobina_id"])
            if "data_inicio" in filtros:
                condicoes.append("data_inicio >= ?")
                params.append(filtros["data_inicio"])
            if "data_fim" in filtros:
                condicoes.append("data_fim <= ?")
                params.append(filtros["data_fim"])

        if condicoes:
            sql += " WHERE " + " AND ".join(condicoes)

        sql += " ORDER BY data_inicio DESC"
        return self.db.buscar_todos(sql, tuple(params))

    def buscar_impressoes(self, termo: str) -> list:
        """Busca impressoes por nome do arquivo ou numero do pedido."""
        sql = """
            SELECT i.*, p.numero as pedido_numero, p.nome as pedido_nome
            FROM impressoes i
            LEFT JOIN pedidos p ON i.pedido_id = p.id
            WHERE i.nome_arquivo LIKE ?
               OR p.numero LIKE ?
               OR p.nome LIKE ?
            ORDER BY i.data_inicio DESC
        """
        padrao = f"%{termo}%"
        return self.db.buscar_todos(sql, (padrao, padrao, padrao))

    def get_impressoes_periodo(self, data_inicio: str, data_fim: str) -> list:
        """Retorna impressoes dentro de um periodo."""
        return self.db.buscar_todos(
            """SELECT * FROM impressoes
               WHERE data_inicio >= ? AND data_fim <= ?
               ORDER BY data_inicio DESC""",
            (data_inicio, data_fim),
        )

    def get_resumo_diario(self) -> dict:
        """Retorna resumo de impressoes do dia."""
        from datetime import date

        hoje = date.today().isoformat()
        impressoes = self.db.buscar_todos(
            """SELECT * FROM impressoes
               WHERE DATE(data_inicio) = ?
               ORDER BY data_inicio""",
            (hoje,),
        )
        custo_total = sum(r["custo_total_centavos"] for r in impressoes)
        return {
            "data": hoje,
            "total_impressoes": len(impressoes),
            "custo_total_centavos": custo_total,
            "impressoes": impressoes,
        }

    def get_resumo_semanal(self) -> dict:
        """Retorna resumo de impressoes dos ultimos 7 dias."""
        from datetime import date, timedelta

        hoje = date.today()
        semana_atras = (hoje - timedelta(days=7)).isoformat()
        impressoes = self.db.buscar_todos(
            """SELECT * FROM impressoes
               WHERE DATE(data_inicio) >= ?
               ORDER BY data_inicio""",
            (semana_atras,),
        )
        custo_total = sum(r["custo_total_centavos"] for r in impressoes)
        return {
            "periodo_inicio": semana_atras,
            "periodo_fim": hoje.isoformat(),
            "total_impressoes": len(impressoes),
            "custo_total_centavos": custo_total,
            "impressoes": impressoes,
        }

    # --- Pedidos ---

    def criar_pedido(self, numero: str, nome: str = "") -> int:
        """Cria um novo pedido e retorna o id."""
        cursor = self.db.executar(
            "INSERT INTO pedidos (numero, nome) VALUES (?, ?)",
            (numero, nome),
        )
        self.db.commitar()
        return cursor.lastrowid

    def get_pedidos(self) -> list:
        """Retorna todos os pedidos."""
        return self.db.buscar_todos(
            "SELECT * FROM pedidos ORDER BY data_criacao DESC"
        )

    def deletar_pedido(self, pedido_id: int):
        """Deleta um pedido."""
        self.db.executar("DELETE FROM pedidos WHERE id = ?", (pedido_id,))
        self.db.commitar()

    # --- Bobinas ---

    def criar_bobina(self, tamanho: str, material: str, tipo: str) -> int:
        """Cria uma nova bobina e retorna o id."""
        cursor = self.db.executar(
            "INSERT INTO bobinas (tamanho, material, tipo) VALUES (?, ?, ?)",
            (tamanho, material, tipo),
        )
        self.db.commitar()
        return cursor.lastrowid

    def get_bobinas(self) -> list:
        """Retorna todas as bobinas."""
        return self.db.buscar_todos("SELECT * FROM bobinas ORDER BY id DESC")

    def atualizar_bobina(
        self, bobina_id: int, tamanho: str, material: str, tipo: str
    ):
        """Atualiza dados de uma bobina."""
        self.db.executar(
            "UPDATE bobinas SET tamanho = ?, material = ?, tipo = ? WHERE id = ?",
            (tamanho, material, tipo, bobina_id),
        )
        self.db.commitar()

    def deletar_bobina(self, bobina_id: int):
        """Deleta uma bobina."""
        self.db.executar("DELETE FROM bobinas WHERE id = ?", (bobina_id,))
        self.db.commitar()

    # --- Metodos antigos (backward compatibility) ---

    def salvar_rodagem(
        self,
        niveis_ini: dict,
        niveis_fim: dict,
        custo_total_centavos: int,
    ):
        """[DEPRECATED] Salva rodagem usando percentuais. Use salvar_impressao()."""
        niveis_ini_ml = {}
        niveis_fim_ml = {}
        config = self.get_configuracoes()
        for cor in self.CORES:
            capacidade = config.get(cor, {}).get("capacidade_ml", 775.0)
            niveis_ini_ml[cor] = (niveis_ini.get(cor, 0) / 100.0) * capacidade
            niveis_fim_ml[cor] = (niveis_fim.get(cor, 0) / 100.0) * capacidade

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
            fim_ml = niveis_fim_ml.get(cor, 0)
            self.db.executar(
                "UPDATE configuracao SET nivel_atual_ml = ? WHERE cor = ?",
                (fim_ml, cor),
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
        impressoes = self.get_impressoes()
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
            "impressoes": [dict(r) for r in impressoes],
        }

    def exportar_sql(self) -> str:
        """Gera script SQL com todos os dados."""
        linhas = [
            "-- DPI Tintas HP - Exportacao SQL",
            "-- Gerado automaticamente",
            "",
            "DELETE FROM configuracao;",
            "DELETE FROM rodagens;",
            "DELETE FROM impressoes;",
            "DELETE FROM pedidos;",
            "DELETE FROM bobinas;",
            "",
        ]

        config = self.get_configuracoes()
        for cor, dados in config.items():
            linhas.append(
                f"INSERT INTO configuracao (cor, capacidade_ml, preco_cartucho_centavos, nivel_atual_ml) "
                f"VALUES ('{cor}', {dados['capacidade_ml']}, {dados['preco_centavos']}, {dados['nivel_atual_ml']:.1f});"
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
