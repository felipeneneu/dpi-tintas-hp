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

    def _create_tables(self):
        cursor = self._conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS configuracao (
                cor TEXT PRIMARY KEY,
                capacidade_ml REAL DEFAULT 100.0,
                preco_cartucho_centavos INTEGER DEFAULT 5000,
                nivel_atual_pct REAL DEFAULT 100.0
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

        cores_existentes = cursor.execute(
            "SELECT cor FROM configuracao"
        ).fetchall()
        cores_existentes = [r["cor"] for r in cores_existentes]

        cores_padrao = ["C", "M", "Y", "K"]
        for cor in cores_padrao:
            if cor not in cores_existentes:
                cursor.execute(
                    """INSERT INTO configuracao (cor, capacidade_ml, preco_cartucho_centavos, nivel_atual_pct)
                       VALUES (?, 100.0, 5000, 100.0)""",
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
