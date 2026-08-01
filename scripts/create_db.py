# -*- coding: utf-8 -*-
"""
Script para criar o banco de dados do DPI Tintas HP.
Usado pelo Inno Setup durante a instalacao.

Argumentos:
    --db-path       Caminho completo para o arquivo do banco de dados
    --config        Caminho para arquivo JSON com configuracoes
    --preco-c       Preco do cartucho Cyan em reais (ex: 50.00)
    --preco-m       Preco do cartucho Magenta em reais
    --preco-y       Preco do cartucho Yellow em reais
    --preco-k       Preco do cartucho Black em reais
    --capacidade    Capacidade dos cartuchos em ml (padrao: 100)
    --nivel         Nivel inicial em % (padrao: 100)
"""

import sqlite3
import argparse
import json
import sys
import os


DEFAULT_CONFIG = {
    "capacidade_ml": 100.0,
    "nivel_atual_pct": 100.0,
    "precos": {
        "C": 50.00,
        "M": 50.00,
        "Y": 50.00,
        "K": 50.00
    }
}


def create_database(db_path: str, config: dict) -> bool:
    """
    Cria o banco de dados SQLite com as tabelas e dados iniciais.

    Args:
        db_path: Caminho completo para o arquivo do banco de dados
        config: Dicionário com as configurações iniciais

    Returns:
        True se criado com sucesso, False caso contrário
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

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

        capacidade = config.get("capacidade_ml", DEFAULT_CONFIG["capacidade_ml"])
        nivel = config.get("nivel_atual_pct", DEFAULT_CONFIG["nivel_atual_pct"])
        precos = config.get("precos", DEFAULT_CONFIG["precos"])

        cores = ["C", "M", "Y", "K"]
        for cor in cores:
            preco_reais = precos.get(cor, 50.00)
            preco_centavos = int(preco_reais * 100)

            cursor.execute("""
                INSERT OR REPLACE INTO configuracao
                (cor, capacidade_ml, preco_cartucho_centavos, nivel_atual_pct)
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
    """Carrega configurações de um arquivo JSON."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao ler arquivo de configuração: {e}", file=sys.stderr)
        return DEFAULT_CONFIG


def load_config_from_args(args) -> dict:
    """Constrói configuração a partir dos argumentos da linha de comando."""
    config = {
        "capacidade_ml": args.capacidade if args.capacidade else DEFAULT_CONFIG["capacidade_ml"],
        "nivel_atual_pct": args.nivel if args.nivel else DEFAULT_CONFIG["nivel_atual_pct"],
        "precos": {
            "C": args.preco_c if args.preco_c else DEFAULT_CONFIG["precos"]["C"],
            "M": args.preco_m if args.preco_m else DEFAULT_CONFIG["precos"]["M"],
            "Y": args.preco_y if args.preco_y else DEFAULT_CONFIG["precos"]["Y"],
            "K": args.preco_k if args.preco_k else DEFAULT_CONFIG["precos"]["K"]
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
        help="Caminho para arquivo JSON com configurações"
    )

    parser.add_argument(
        "--preco-c",
        type=float,
        help="Preço do cartucho Cyan em reais"
    )
    parser.add_argument(
        "--preco-m",
        type=float,
        help="Preço do cartucho Magenta em reais"
    )
    parser.add_argument(
        "--preco-y",
        type=float,
        help="Preço do cartucho Yellow em reais"
    )
    parser.add_argument(
        "--preco-k",
        type=float,
        help="Preço do cartucho Black em reais"
    )
    parser.add_argument(
        "--capacidade",
        type=float,
        help="Capacidade dos cartuchos em ml (padrão: 100)"
    )
    parser.add_argument(
        "--nivel",
        type=float,
        help="Nível inicial em %% (padrão: 100)"
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
