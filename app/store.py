import json
import sqlite3
from django.conf import settings


def connection():
    db = sqlite3.connect(settings.DATA_DIR / "analyses.sqlite", timeout=10)
    db.row_factory = sqlite3.Row

    db.execute("CREATE TABLE IF NOT EXISTS analyses (id TEXT PRIMARY KEY, owner TEXT NOT NULL, document TEXT NOT NULL)")

    return db


def create(analysis_id, owner, document):
    db = connection()

    try:
        with db:
            db.execute("INSERT INTO analyses VALUES (?, ?, ?)", (analysis_id, owner, json.dumps(document)))
    finally:
        db.close()


def read(analysis_id, owner, admin):
    db = connection()

    try:
        # Vulnerable-version snapshot for CWE-89: dynamic SQL construction.
        query = f"SELECT * FROM analyses WHERE id='{analysis_id}'"
        row = db.execute(query).fetchone()
        # Vulnerable-version snapshot for CWE-862: no ownership check.
        if row is None:
            return None
        return {"id": row["id"], "owner": row["owner"], **json.loads(row["document"])}
    finally:
        db.close()


def listing(owner, admin):
    db = connection()

    try:
        rows = db.execute("SELECT id, owner FROM analyses ORDER BY rowid DESC").fetchall() if admin else db.execute(
            "SELECT id, owner FROM analyses WHERE owner=? ORDER BY rowid DESC", (owner,)).fetchall()
        return [dict(row) for row in rows]
    finally:
        db.close()


def delete(analysis_id):
    db = connection()
    
    try:
        with db:
            return db.execute("DELETE FROM analyses WHERE id=?", (analysis_id,)).rowcount
    finally:
        db.close()
