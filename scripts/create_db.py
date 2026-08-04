# -*- coding: utf-8 -*-
"""
Script para criar o banco de dados do DPI Tintas HP.
Usado pelo Inno Setup durante a instalacao.

Se o banco ja existe com dados, o script NAO sobrescreve.
A migracao e feita pelo app na primeira execucao.

Argumentos:
    --db-path       Caminho completo para o arquivo do banco de dados
    --config        Caminho para arquivo JSON com configuracoes
    --preco-c       Preco do cartucho Cyan em reais (ex: 50.00)
    --preco-m       Preco do cartucho Magenta em reais
    --preco-y       Preco do cartucho Yellow em reais
    --preco-k       Preco do cartucho Black em reais
    --preco-lc      Preco do cartucho Light Cyan em reais
    --preco-lm      Preco do cartucho Light Magenta em reais
    --preco-op      Preco do cartucho Opaca em reais
    --capacidade    Capacidade dos cartuchos em ml (padrao: 775)
    --nivel         Nivel inicial em ml (padrao: 775)
"""

import sqlite3
import argparse
import json
import sys
import os


DEFAULT_CONFIG = {
    "capacidade_ml": 775.0,
    "nivel_atual_ml": 775.0,
    "precos": {
        "C": 50.00,
        "M": 50.00,
        "Y": 50.00,
        "K": 50.00,
        "LC": 50.00,
        "LM": 50.00,
        "OP": 50.00
    }
}


def banco_ja_existe_com_dados(db_path: str) -> bool:
    """Verifica se o banco ja existe e tem dados de configuracao."""
    if not os.path.exists(db_path):
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM configuracao")
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    except Exception:
        return False


def create_database(db_path: str, config: dict) -> bool:
    """
    Cria o banco de dados SQLite com as tabelas e dados iniciais.

    Se o banco ja existe com dados, NAO sobrescreve.
    A migracao e feita pelo app na primeira execucao.

    Args:
        db_path: Caminho completo para o arquivo do banco de dados
        config: Dicionario com as configuracoes iniciais

    Returns:
        True se criado com sucesso ou ja existia, False caso contrario
    """
    if banco_ja_existe_com_dados(db_path):
        print(f"Banco existente detectado. Pulando criacao: {db_path}")
        return True

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

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

        capacidade = config.get("capacidade_ml", DEFAULT_CONFIG["capacidade_ml"])
        nivel = config.get("nivel_atual_ml", DEFAULT_CONFIG["nivel_atual_ml"])
        precos = config.get("precos", DEFAULT_CONFIG["precos"])

        cores = ["C", "M", "Y", "K", "LC", "LM", "OP"]
        for cor in cores:
            preco_reais = precos.get(cor, 50.00)
            preco_centavos = int(preco_reais * 100)

            cursor.execute("""
                INSERT OR REPLACE INTO configuracao
                (cor, capacidade_ml, preco_cartucho_centavos, nivel_atual_ml)
                VALUES (?, ?, ?, ?)
            """, (cor, capacidade, preco_centavos, nivel))

        conn.commit()
        conn.close()

        print(f"Banco de dados criado: {db_path}")
        return True

    except Exception as e:
        print(f"Erro ao criar banco de dados: {e}", file=sys.stderr)
        return False


def load_config_from_file(config_path: str) -> dict:
    """Carrega configuracoes de um arquivo JSON."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao ler arquivo de configuracao: {e}", file=sys.stderr)
        return DEFAULT_CONFIG


def load_config_from_args(args) -> dict:
    """Constrói configuracao a partir dos argumentos da linha de comando."""
    config = {
        "capacidade_ml": args.capacidade if args.capacidade else DEFAULT_CONFIG["capacidade_ml"],
        "nivel_atual_ml": args.nivel if args.nivel else DEFAULT_CONFIG["nivel_atual_ml"],
        "precos": {
            "C": args.preco_c if args.preco_c else DEFAULT_CONFIG["precos"]["C"],
            "M": args.preco_m if args.preco_m else DEFAULT_CONFIG["precos"]["M"],
            "Y": args.preco_y if args.preco_y else DEFAULT_CONFIG["precos"]["Y"],
            "K": args.preco_k if args.preco_k else DEFAULT_CONFIG["precos"]["K"],
            "LC": args.preco_lc if args.preco_lc else DEFAULT_CONFIG["precos"]["LC"],
            "LM": args.preco_lm if args.preco_lm else DEFAULT_CONFIG["precos"]["LM"],
            "OP": args.preco_op if args.preco_op else DEFAULT_CONFIG["precos"]["OP"]
        }
    }
    return config


def main():
    parser = argparse.ArgumentParser(
        description="Cria o banco de dados do DPI Tintas HP"
    )

    parser.add_argument(
        "--db-path",
        required=True,
        help="Caminho completo para o arquivo do banco de dados"
    )

    parser.add_argument(
        "--config",
        help="Caminho para arquivo JSON com configuracoes"
    )

    parser.add_argument(
        "--preco-c",
        type=float,
        help="Preco do cartucho Cyan em reais"
    )
    parser.add_argument(
        "--preco-m",
        type=float,
        help="Preco do cartucho Magenta em reais"
    )
    parser.add_argument(
        "--preco-y",
        type=float,
        help="Preco do cartucho Yellow em reais"
    )
    parser.add_argument(
        "--preco-k",
        type=float,
        help="Preco do cartucho Black em reais"
    )
    parser.add_argument(
        "--preco-lc",
        type=float,
        help="Preco do cartucho Light Cyan em reais"
    )
    parser.add_argument(
        "--preco-lm",
        type=float,
        help="Preco do cartucho Light Magenta em reais"
    )
    parser.add_argument(
        "--preco-op",
        type=float,
        help="Preco do cartucho Opaca em reais"
    )
    parser.add_argument(
        "--capacidade",
        type=float,
        help="Capacidade dos cartuchos em ml (padrao: 775)"
    )
    parser.add_argument(
        "--nivel",
        type=float,
        help="Nivel inicial em ml (padrao: 775)"
    )

    args = parser.parse_args()

    if args.config:
        config = load_config_from_file(args.config)
    else:
        config = load_config_from_args(args)

    db_dir = os.path.dirname(args.db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    success = create_database(args.db_path, config)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
