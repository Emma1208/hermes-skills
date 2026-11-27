#!/usr/bin/env python3
"""Base de données du bot pédagogique — classes commerciales 1-4."""

import json
import sqlite3
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

DB_DIR = Path(__file__).parent / "data"
DB_PATH = DB_DIR / "pedagogique.db"


def _conn() -> sqlite3.Connection:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(str(DB_PATH))
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    c.execute("PRAGMA foreign_keys=ON")
    return c


# ── INIT ──────────────────────────────────────────────────────────

def init() -> None:
    with _conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT UNIQUE NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS branches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            classe_id INTEGER NOT NULL REFERENCES classes(id),
            nom TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            UNIQUE(classe_id, nom)
        );

        CREATE TABLE IF NOT EXISTS calendrier (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            classe_id INTEGER NOT NULL REFERENCES classes(id),
            branche_id INTEGER NOT NULL REFERENCES branches(id),
            date TEXT NOT NULL,
            heure_debut TEXT,
            heure_fin TEXT,
            sujet TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS fiches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            classe_id INTEGER NOT NULL REFERENCES classes(id),
            branche_id INTEGER NOT NULL REFERENCES branches(id),
            date TEXT NOT NULL,
            heure_debut TEXT,
            heure_fin TEXT,
            sujet TEXT NOT NULL,
            objectif TEXT,
            methodes TEXT,
            reference TEXT,
            revision_question TEXT,
            revision_reponse TEXT,
            motivation TEXT,
            annonce_sujet TEXT,
            analyse TEXT,
            synthese TEXT,
            evaluation TEXT,
            pdf_path TEXT,
            raw_llm TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS previsions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            classe_id INTEGER NOT NULL REFERENCES classes(id),
            branche_id INTEGER NOT NULL REFERENCES branches(id),
            date TEXT NOT NULL,
            heure_debut TEXT,
            heure_fin TEXT,
            sujet TEXT,
            fiche_id INTEGER REFERENCES fiches(id),
            created_at TEXT DEFAULT (datetime('now'))
        );
        """)
        # Insérer les classes par défaut
        for nom in ["Commerciale 1", "Commerciale 2", "Commerciale 3", "Commerciale 4"]:
            c.execute("INSERT OR IGNORE INTO classes(nom) VALUES(?)", (nom,))


# ── CLASSES ───────────────────────────────────────────────────────

def lister_classes() -> List[Dict[str, Any]]:
    with _conn() as c:
        rows = c.execute("SELECT * FROM classes ORDER BY nom").fetchall()
        return [dict(r) for r in rows]


def ajouter_classe(nom: str) -> int:
    with _conn() as c:
        c.execute("INSERT OR IGNORE INTO classes(nom) VALUES(?)", (nom.strip(),))
        row = c.execute("SELECT id FROM classes WHERE nom=?", (nom.strip(),)).fetchone()
        return row["id"] if row else 0


# ── BRANCHES ──────────────────────────────────────────────────────

def lister_branches(classe_id: int) -> List[Dict[str, Any]]:
    with _conn() as c:
        rows = c.execute(
            "SELECT * FROM branches WHERE classe_id=? ORDER BY nom", (classe_id,)
        ).fetchall()
        return [dict(r) for r in rows]


def ajouter_branche(classe_id: int, nom: str) -> int:
    with _conn() as c:
        c.execute(
            "INSERT OR IGNORE INTO branches(classe_id, nom) VALUES(?,?)",
            (classe_id, nom.strip()),
        )
        row = c.execute(
            "SELECT id FROM branches WHERE classe_id=? AND nom=?",
            (classe_id, nom.strip()),
        ).fetchone()
        return row["id"] if row else 0


# ── CALENDRIER ────────────────────────────────────────────────────

def ajouter_calendrier(
    classe_id: int,
    branche_id: int,
    date_str: str,
    heure_debut: Optional[str] = None,
    heure_fin: Optional[str] = None,
    sujet: Optional[str] = None,
) -> int:
    with _conn() as c:
        c.execute(
            """INSERT INTO calendrier(classe_id, branche_id, date, heure_debut, heure_fin, sujet)
               VALUES(?,?,?,?,?,?)""",
            (classe_id, branche_id, date_str, heure_debut, heure_fin, sujet),
        )
        return c.lastrowid or 0


def importer_calendrier(classe_id: int, lignes: List[Dict]) -> int:
    """Importe plusieurs entrées à la fois.
    lignes = [{"branche_id": 1, "date": "2026-09-15", "debut": "8h", "fin": "10h", "sujet": ""}]
    """
    count = 0
    with _conn() as c:
        for ligne in lignes:
            c.execute(
                """INSERT INTO calendrier(classe_id, branche_id, date, heure_debut, heure_fin, sujet)
                   VALUES(?,?,?,?,?,?)""",
                (
                    classe_id,
                    ligne["branche_id"],
                    ligne["date"],
                    ligne.get("debut"),
                    ligne.get("fin"),
                    ligne.get("sujet", ""),
                ),
            )
            count += 1
    return count


def lister_calendrier(
    classe_id: int,
    date_debut: Optional[str] = None,
    date_fin: Optional[str] = None,
) -> List[Dict[str, Any]]:
    with _conn() as c:
        query = """SELECT c.*, b.nom as branche_nom, cl.nom as classe_nom
                   FROM calendrier c
                   JOIN branches b ON c.branche_id = b.id
                   JOIN classes cl ON c.classe_id = cl.id
                   WHERE c.classe_id = ?"""
        params: List = [classe_id]
        if date_debut:
            query += " AND c.date >= ?"
            params.append(date_debut)
        if date_fin:
            query += " AND c.date <= ?"
            params.append(date_fin)
        query += " ORDER BY c.date, c.heure_debut"
        rows = c.execute(query, params).fetchall()
        return [dict(r) for r in rows]


def previsions_semaine(classe_id: int, debut: str, fin: str) -> List[Dict]:
    """Renvoie les entrées du calendrier entre deux dates, avec le statut fiche."""
    with _conn() as c:
        rows = c.execute(
            """SELECT cal.*, b.nom as branche_nom, cl.nom as classe_nom,
                      CASE WHEN f.id IS NOT NULL THEN 1 ELSE 0 END as fiche_existe
               FROM calendrier cal
               JOIN branches b ON cal.branche_id = b.id
               JOIN classes cl ON cal.classe_id = cl.id
               LEFT JOIN fiches f ON f.classe_id = cal.classe_id
                                   AND f.branche_id = cal.branche_id
                                   AND f.date = cal.date
                                   AND f.sujet = COALESCE(cal.sujet, f.sujet)
               WHERE cal.classe_id = ? AND cal.date >= ? AND cal.date <= ?
               ORDER BY cal.date, cal.heure_debut""",
            (classe_id, debut, fin),
        ).fetchall()
        return [dict(r) for r in rows]


# ── FICHES ────────────────────────────────────────────────────────

def sauvegarder_fiche(
    classe_id: int,
    branche_id: int,
    date_str: str,
    sujet: str,
    objectif: Optional[str] = None,
    methodes: Optional[str] = None,
    reference: Optional[str] = None,
    revision_question: Optional[str] = None,
    revision_reponse: Optional[str] = None,
    motivation: Optional[str] = None,
    annonce_sujet: Optional[str] = None,
    analyse: Optional[str] = None,
    synthese: Optional[str] = None,
    evaluation: Optional[str] = None,
    heure_debut: Optional[str] = None,
    heure_fin: Optional[str] = None,
    pdf_path: Optional[str] = None,
    raw_llm: Optional[str] = None,
) -> int:
    """Sauvegarde ou met à jour une fiche."""
    with _conn() as c:
        existing = c.execute(
            "SELECT id FROM fiches WHERE classe_id=? AND branche_id=? AND date=? AND sujet=?",
            (classe_id, branche_id, date_str, sujet),
        ).fetchone()

        if existing:
            c.execute(
                """UPDATE fiches SET objectif=?, methodes=?, reference=?,
                   revision_question=?, revision_reponse=?, motivation=?, annonce_sujet=?,
                   analyse=?, synthese=?, evaluation=?, pdf_path=?, raw_llm=?
                   WHERE id=?""",
                (
                    objectif, methodes, reference,
                    revision_question, revision_reponse, motivation, annonce_sujet,
                    analyse, synthese, evaluation, pdf_path, raw_llm,
                    existing["id"],
                ),
            )
            return existing["id"]
        else:
            c.execute(
                """INSERT INTO fiches(classe_id, branche_id, date, heure_debut, heure_fin,
                   sujet, objectif, methodes, reference,
                   revision_question, revision_reponse, motivation, annonce_sujet,
                   analyse, synthese, evaluation, pdf_path, raw_llm)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    classe_id, branche_id, date_str, heure_debut, heure_fin,
                    sujet, objectif, methodes, reference,
                    revision_question, revision_reponse, motivation, annonce_sujet,
                    analyse, synthese, evaluation, pdf_path, raw_llm,
                ),
            )
            return c.lastrowid or 0


def lister_fiches(classe_id: Optional[int] = None, limit: int = 10) -> List[Dict]:
    with _conn() as c:
        query = """SELECT f.*, b.nom as branche_nom, cl.nom as classe_nom
                   FROM fiches f
                   JOIN branches b ON f.branche_id = b.id
                   JOIN classes cl ON f.classe_id = cl.id"""
        params: List = []
        if classe_id is not None:
            query += " WHERE f.classe_id = ?"
            params.append(classe_id)
        query += " ORDER BY f.created_at DESC LIMIT ?"
        params.append(limit)
        rows = c.execute(query, params).fetchall()
        return [dict(r) for r in rows]


def chercher_fiches(
    classe_id: Optional[int] = None,
    branche_id: Optional[int] = None,
    q: Optional[str] = None,
    limit: int = 10,
) -> List[Dict]:
    with _conn() as c:
        conditions = []
        params: List = []
        if classe_id:
            conditions.append("f.classe_id = ?")
            params.append(classe_id)
        if branche_id:
            conditions.append("f.branche_id = ?")
            params.append(branche_id)
        if q:
            conditions.append("(f.sujet LIKE ? OR f.objectif LIKE ?)")
            params.extend([f"%{q}%", f"%{q}%"])

        where = " AND ".join(conditions) if conditions else "1"
        rows = c.execute(
            f"""SELECT f.*, b.nom as branche_nom, cl.nom as classe_nom
                FROM fiches f
                JOIN branches b ON f.branche_id = b.id
                JOIN classes cl ON f.classe_id = cl.id
                WHERE {where}
                ORDER BY f.date DESC LIMIT ?""",
            params + [limit],
        ).fetchall()
        return [dict(r) for r in rows]


def get_fiche(fiche_id: int) -> Optional[Dict]:
    with _conn() as c:
        row = c.execute(
            """SELECT f.*, b.nom as branche_nom, cl.nom as classe_nom
               FROM fiches f
               JOIN branches b ON f.branche_id = b.id
               JOIN classes cl ON f.classe_id = cl.id
               WHERE f.id=?""",
            (fiche_id,),
        ).fetchone()
        return dict(row) if row else None


# ── UTILS ─────────────────────────────────────────────────────────

def find_or_create_branche(classe_id: int, nom: str) -> int:
    """Trouve ou crée une branche, retourne son id."""
    with _conn() as c:
        row = c.execute(
            "SELECT id FROM branches WHERE classe_id=? AND nom=?",
            (classe_id, nom.strip()),
        ).fetchone()
        if row:
            return row["id"]
        c.execute(
            "INSERT INTO branches(classe_id, nom) VALUES(?,?)",
            (classe_id, nom.strip()),
        )
        return c.lastrowid or 0
