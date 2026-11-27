#!/usr/bin/env python3
"""SQLite local pour trades, positions, scores, logs, stats."""
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).with_name("bot.db")


def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init():
    with conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT,
            symbol TEXT,
            side TEXT,
            qty REAL,
            price REAL,
            fee REAL,
            order_id TEXT
        );
        CREATE TABLE IF NOT EXISTS positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            opened_at TEXT,
            symbol TEXT,
            side TEXT,
            entry_price REAL,
            qty REAL,
            status TEXT
        );
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT,
            symbol TEXT,
            score INTEGER,
            tech INTEGER,
            fund INTEGER,
            sent INTEGER
        );
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT,
            level TEXT,
            msg TEXT
        );
        CREATE TABLE IF NOT EXISTS stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            pnl REAL,
            trades_count INTEGER
        );
        """)
        log("INFO", "database initialized")


def log(level: str, msg: str):
    with conn() as c:
        c.execute("INSERT INTO logs(ts,level,msg) VALUES(?,?,?)",
                  (datetime.utcnow().isoformat(), level, msg))


def add_trade(symbol, side, qty, price, fee, order_id):
    with conn() as c:
        c.execute("INSERT INTO trades(ts,symbol,side,qty,price,fee,order_id) VALUES(?,?,?,?,?,?,?)",
                  (datetime.utcnow().isoformat(), symbol, side, qty, price, fee, order_id))


def add_score(symbol, score, tech, fund, sent):
    with conn() as c:
        c.execute("INSERT INTO scores(ts,symbol,score,tech,fund,sent) VALUES(?,?,?,?,?,?)",
                  (datetime.utcnow().isoformat(), symbol, int(score), int(tech), int(fund), int(sent)))
