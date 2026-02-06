import sqlite3
import tempfile
import os
import pytest
from app.db.schema import create_tables

@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setenv('DB_PATH', str(db_path))

    create_tables()

    yield