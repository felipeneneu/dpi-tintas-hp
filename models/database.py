import sqlite3
import os
from config.theme import DPITheme


class Database:
    _instance = None
    _conn = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.db_path = DPITheme.DB_PATH
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._create_tables()

    def _migrar_schema(self, cursor):
        """Migra schema antigo para novo, preservando dados do usuario.

        Cenarios tratados:
        - Banco v1 antigo (4 cores, nivel_atual_pct, capacidade 100ml)
        - Banco v1 parcialmente migrado (nivel_atual_ml existe, mas cores faltam)
        - Banco v2 completo (nao faz nada)
        """
        try:
            cursor.execute("PRAGMA table_info(configuracao)")
            colunas = [row[1] for row in cursor.fetchall()]

            if "nivel_atual_pct" in colunas and "nivel_atual_ml" not in colunas:
                cursor.execute(
                    "ALTER TABLE configuracao RENAME COLUMN nivel_atual_pct TO nivel_atual_ml"
                )
                cursor.execute(
                    "UPDATE configuracao "
                    "SET nivel_atual_ml = (nivel_atual_ml / 100.0) * 775.0, "
                    "    capacidade_ml = 775.0 "
                    "WHERE capacidade_ml <= 100.0"
                )
        except Exception:
            pass

        try:
            cores_existentes = [
                r["cor"] for r in cursor.execute("SELECT cor FROM configuracao").fetchall()
            ]
            for cor in ["C", "M", "Y", "K", "LC", "LM", "OP"]:
                if cor not in cores_existentes:
                    cursor.execute(
                        "INSERT INTO configuracao "
                        "(cor, capacidade_ml, preco_cartucho_centavos, nivel_atual_ml) "
                        "VALUES (?, 775.0, 5000, 775.0)",
                        (cor,),
                    )
        except Exception:
            pass

    def _create_tables(self):
        cursor = self._conn.cursor()

        self._migrar_schema(cursor)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS configuracao (
                cor TEXT PRIMARY KEY,
                capacidade_ml REAL DEFAULT 775.0,
                preco_cartucho_centavos INTEGER DEFAULT 5000,
                nivel_atual_ml REAL DEFAULT 775.0
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rodagens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                c_ini REAL, m_ini REAL, y_ini REAL, k_ini REAL,
                c_fim REAL, m_fim REAL, y_fim REAL, k_fim REAL,
                custo_total_centavos INTEGER DEFAULT 0
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero TEXT NOT NULL,
                nome TEXT DEFAULT '',
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bobinas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tamanho TEXT DEFAULT '',
                material TEXT DEFAULT '',
                tipo TEXT DEFAULT ''
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS impressoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pedido_id INTEGER,
                bobina_id INTEGER,
                nome_arquivo TEXT DEFAULT '',
                data_inicio TIMESTAMP,
                data_fim TIMESTAMP,
                duracao_segundos INTEGER DEFAULT 0,
                c_ini_ml REAL DEFAULT 0, m_ini_ml REAL DEFAULT 0,
                y_ini_ml REAL DEFAULT 0, k_ini_ml REAL DEFAULT 0,
                lc_ini_ml REAL DEFAULT 0, lm_ini_ml REAL DEFAULT 0, op_ini_ml REAL DEFAULT 0,
                c_fim_ml REAL DEFAULT 0, m_fim_ml REAL DEFAULT 0,
                y_fim_ml REAL DEFAULT 0, k_fim_ml REAL DEFAULT 0,
                lc_fim_ml REAL DEFAULT 0, lm_fim_ml REAL DEFAULT 0, op_fim_ml REAL DEFAULT 0,
                custo_total_centavos INTEGER DEFAULT 0,
                FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
                FOREIGN KEY (bobina_id) REFERENCES bobinas(id)
            )
        """)

        cores_existentes = cursor.execute(
            "SELECT cor FROM configuracao"
        ).fetchall()
        cores_existentes = [r["cor"] for r in cores_existentes]

        cores_padrao = ["C", "M", "Y", "K", "LC", "LM", "OP"]
        for cor in cores_padrao:
            if cor not in cores_existentes:
                cursor.execute(
                    """INSERT INTO configuracao (cor, capacidade_ml, preco_cartucho_centavos, nivel_atual_ml)
                       VALUES (?, 775.0, 5000, 775.0)""",
                    (cor,),
                )

        self._conn.commit()

    def executar(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        return self._conn.cursor().execute(sql, params)

    def commitar(self):
        self._conn.commit()

    def buscar_todos(self, sql: str, params: tuple = ()) -> list:
        return self._conn.cursor().execute(sql, params).fetchall()

    def buscar_um(self, sql: str, params: tuple = ()) -> dict | None:
        row = self._conn.cursor().execute(sql, params).fetchone()
        return dict(row) if row else None

    def fechar(self):
        if self._conn:
            self._conn.close()
