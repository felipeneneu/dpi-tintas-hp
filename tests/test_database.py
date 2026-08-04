from models.database import Database


class TestDatabaseSingleton:
    def test_singleton_returns_same_instance(self, fresh_db):
        from models.database import Database

        db1 = Database.get_instance()
        db2 = Database.get_instance()
        assert db1 is db2

    def test_singleton_resets(self, reset_db_singleton):
        from models.database import Database

        db1 = Database.get_instance()
        Database._instance = None
        db2 = Database.get_instance()
        assert db1 is not db2


class TestDatabaseTables:
    def test_tabela_configuracao_existe(self, fresh_db):
        cursor = fresh_db._conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='configuracao'"
        )
        assert cursor.fetchone() is not None

    def test_tabela_rodagens_existe(self, fresh_db):
        cursor = fresh_db._conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='rodagens'"
        )
        assert cursor.fetchone() is not None

    def test_tabela_pedidos_existe(self, fresh_db):
        cursor = fresh_db._conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='pedidos'"
        )
        assert cursor.fetchone() is not None

    def test_tabela_bobinas_existe(self, fresh_db):
        cursor = fresh_db._conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='bobinas'"
        )
        assert cursor.fetchone() is not None

    def test_tabela_impressoes_existe(self, fresh_db):
        cursor = fresh_db._conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='impressoes'"
        )
        assert cursor.fetchone() is not None

    def test_cores_padrao_inseridas(self, fresh_db):
        rows = fresh_db.buscar_todos("SELECT cor FROM configuracao ORDER BY cor")
        cores = [r["cor"] for r in rows]
        assert cores == ["C", "K", "LC", "LM", "M", "OP", "Y"]

    def test_configuracao_defaults(self, fresh_db):
        row = fresh_db.buscar_um(
            "SELECT * FROM configuracao WHERE cor = ?", ("C",)
        )
        assert row["capacidade_ml"] == 775.0
        assert row["preco_cartucho_centavos"] == 5000
        assert row["nivel_atual_ml"] == 775.0


class TestDatabaseCRUD:
    def test_executar_e_commitar(self, fresh_db):
        fresh_db.executar(
            "UPDATE configuracao SET nivel_atual_ml = ? WHERE cor = ?",
            (600.0, "C"),
        )
        fresh_db.commitar()

        row = fresh_db.buscar_um(
            "SELECT nivel_atual_ml FROM configuracao WHERE cor = ?", ("C",)
        )
        assert row["nivel_atual_ml"] == 600.0

    def test_buscar_um_retorna_none_se_nao_encontra(self, fresh_db):
        row = fresh_db.buscar_um(
            "SELECT * FROM configuracao WHERE cor = ?", ("X",)
        )
        assert row is None

    def test_buscar_todos(self, fresh_db):
        rows = fresh_db.buscar_todos("SELECT * FROM configuracao")
        assert len(rows) == 7

    def test_insert_rodagem(self, fresh_db):
        fresh_db.executar(
            """INSERT INTO rodagens
               (c_ini, m_ini, y_ini, k_ini, c_fim, m_fim, y_fim, k_fim, custo_total_centavos)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (100, 100, 100, 100, 80, 90, 70, 85, 1500),
        )
        fresh_db.commitar()

        row = fresh_db.buscar_um("SELECT * FROM rodagens ORDER BY id DESC LIMIT 1")
        assert row is not None
        assert row["c_ini"] == 100
        assert row["c_fim"] == 80
        assert row["custo_total_centavos"] == 1500

    def test_insert_pedido(self, fresh_db):
        fresh_db.executar(
            "INSERT INTO pedidos (numero, nome) VALUES (?, ?)",
            ("PED-001", "Cliente ABC"),
        )
        fresh_db.commitar()

        row = fresh_db.buscar_um("SELECT * FROM pedidos ORDER BY id DESC LIMIT 1")
        assert row is not None
        assert row["numero"] == "PED-001"
        assert row["nome"] == "Cliente ABC"

    def test_insert_bobina(self, fresh_db):
        fresh_db.executar(
            "INSERT INTO bobinas (tamanho, material, tipo) VALUES (?, ?, ?)",
            ("60cm", "Vinil", "Brilho"),
        )
        fresh_db.commitar()

        row = fresh_db.buscar_um("SELECT * FROM bobinas ORDER BY id DESC LIMIT 1")
        assert row is not None
        assert row["tamanho"] == "60cm"
        assert row["material"] == "Vinil"
        assert row["tipo"] == "Brilho"

    def test_insert_impressao(self, fresh_db):
        fresh_db.executar(
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
                None, None, "arquivo.pdf", "2026-01-01T10:00:00", "2026-01-01T10:05:00",
                300,
                775, 775, 775, 775, 775, 775, 775,
                700, 750, 720, 760, 770, 765, 775,
                2500,
            ),
        )
        fresh_db.commitar()

        row = fresh_db.buscar_um("SELECT * FROM impressoes ORDER BY id DESC LIMIT 1")
        assert row is not None
        assert row["nome_arquivo"] == "arquivo.pdf"
        assert row["c_ini_ml"] == 775
        assert row["c_fim_ml"] == 700
        assert row["custo_total_centavos"] == 2500


class TestDatabaseMigracao:
    def test_migracao_v1_para_v2(self, fresh_db):
        cursor = fresh_db._conn.cursor()

        cursor.execute("DROP TABLE IF EXISTS configuracao")
        cursor.execute("""
            CREATE TABLE configuracao (
                cor TEXT PRIMARY KEY,
                capacidade_ml REAL DEFAULT 100.0,
                preco_cartucho_centavos INTEGER DEFAULT 5000,
                nivel_atual_pct REAL DEFAULT 100.0
            )
        """)
        for cor, pct in [("C", 99.0), ("M", 98.0), ("Y", 76.0), ("K", 50.0)]:
            cursor.execute(
                "INSERT INTO configuracao (cor, capacidade_ml, nivel_atual_pct) VALUES (?, 100.0, ?)",
                (cor, pct),
            )
        fresh_db._conn.commit()

        fresh_db._migrar_schema(cursor)

        row = cursor.execute("SELECT nivel_atual_ml FROM configuracao WHERE cor = 'C'").fetchone()
        assert row is not None
        assert abs(row[0] - 767.25) < 0.1

        cores = [r[0] for r in cursor.execute("SELECT cor FROM configuracao ORDER BY cor").fetchall()]
        assert "LC" in cores
        assert "LM" in cores
        assert "OP" in cores

    def test_migracao_preserva_dados_existentes(self, fresh_db):
        cursor = fresh_db._conn.cursor()

        cursor.execute("DROP TABLE IF EXISTS configuracao")
        cursor.execute("""
            CREATE TABLE configuracao (
                cor TEXT PRIMARY KEY,
                capacidade_ml REAL DEFAULT 100.0,
                preco_cartucho_centavos INTEGER DEFAULT 8000,
                nivel_atual_pct REAL DEFAULT 100.0
            )
        """)
        cursor.execute(
            "INSERT INTO configuracao (cor, capacidade_ml, preco_cartucho_centavos, nivel_atual_pct) VALUES (?, 200.0, 9000, 75.0)",
            ("C",),
        )
        fresh_db._conn.commit()

        fresh_db._migrar_schema(cursor)

        row = cursor.execute("SELECT * FROM configuracao WHERE cor = 'C'").fetchone()
        assert row is not None
        assert row[1] == 200.0
        assert row[2] == 9000
        assert row[3] == 75.0

    def test_migracao_converte_capacidade_antiga(self, fresh_db):
        cursor = fresh_db._conn.cursor()

        cursor.execute("DROP TABLE IF EXISTS configuracao")
        cursor.execute("""
            CREATE TABLE configuracao (
                cor TEXT PRIMARY KEY,
                capacidade_ml REAL DEFAULT 100.0,
                preco_cartucho_centavos INTEGER DEFAULT 5000,
                nivel_atual_pct REAL DEFAULT 100.0
            )
        """)
        cursor.execute(
            "INSERT INTO configuracao (cor, capacidade_ml, nivel_atual_pct) VALUES (?, 100.0, 80.0)",
            ("M",),
        )
        fresh_db._conn.commit()

        fresh_db._migrar_schema(cursor)

        row = cursor.execute("SELECT * FROM configuracao WHERE cor = 'M'").fetchone()
        assert row is not None
        assert row[1] == 775.0
        assert abs(row[3] - 620.0) < 0.1
