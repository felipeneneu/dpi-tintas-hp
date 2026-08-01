import sqlite3
import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture(autouse=True)
def reset_db_singleton():
    """Reseta o singleton Database antes e depois de cada teste."""
    from models.database import Database

    Database._instance = None
    Database._conn = None
    yield
    Database._instance = None
    Database._conn = None


@pytest.fixture
def in_memory_db():
    """Cria um Database conectado a SQLite em memoria."""
    from models.database import Database

    db = Database.__new__(Database)
    db.db_path = ":memory:"
    db._conn = sqlite3.connect(":memory:")
    db._conn.row_factory = sqlite3.Row
    db._create_tables()

    Database._instance = db
    return db


@pytest.fixture
def fresh_db():
    """Cria Database com conexao real em memoria e injeta como singleton."""
    from models.database import Database

    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row

    db = Database.__new__(Database)
    db.db_path = ":memory:"
    db._conn = conn
    db._create_tables()

    Database._instance = db
    return db


@pytest.fixture
def model(fresh_db):
    """Cria TintaModel usando DB em memoria."""
    from models.tinta_model import TintaModel

    m = TintaModel.__new__(TintaModel)
    m.db = fresh_db
    return m
