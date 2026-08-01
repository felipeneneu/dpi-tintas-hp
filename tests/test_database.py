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

    def test_cores_padrao_inseridas(self, fresh_db):
        rows = fresh_db.buscar_todos("SELECT cor FROM configuracao ORDER BY cor")
        cores = [r["cor"] for r in rows]
        assert cores == ["C", "K", "M", "Y"]

    def test_configuracao_defaults(self, fresh_db):
        row = fresh_db.buscar_um(
            "SELECT * FROM configuracao WHERE cor = ?", ("C",)
        )
        assert row["capacidade_ml"] == 100.0
        assert row["preco_cartucho_centavos"] == 5000
        assert row["nivel_atual_pct"] == 100.0


class TestDatabaseCRUD:
    def test_executar_e_commitar(self, fresh_db):
        fresh_db.executar(
            "UPDATE configuracao SET nivel_atual_pct = ? WHERE cor = ?",
            (75.0, "C"),
        )
        fresh_db.commitar()

        row = fresh_db.buscar_um(
            "SELECT nivel_atual_pct FROM configuracao WHERE cor = ?", ("C",)
        )
        assert row["nivel_atual_pct"] == 75.0

    def test_buscar_um_retorna_none_se_nao_encontra(self, fresh_db):
        row = fresh_db.buscar_um(
            "SELECT * FROM configuracao WHERE cor = ?", ("X",)
        )
        assert row is None

    def test_buscar_todos(self, fresh_db):
        rows = fresh_db.buscar_todos("SELECT * FROM configuracao")
        assert len(rows) == 4

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
