"""Esquema do banco SQLite."""
import os
import sqlite3

from cienciometria import config

ESQUEMA = """
CREATE TABLE IF NOT EXISTS trabalhos (
    id TEXT PRIMARY KEY, titulo TEXT, ano INTEGER, citacoes INTEGER,
    conceito_principal TEXT, exportado INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS autorias (
    trabalho_id TEXT, autor_id TEXT, autor_nome TEXT,
    instituicao_id TEXT, instituicao_nome TEXT, pais TEXT);
CREATE TABLE IF NOT EXISTS conceitos (
    id TEXT PRIMARY KEY, nome TEXT, nivel INTEGER, ancestrais TEXT);
CREATE TABLE IF NOT EXISTS conceitos_trabalho (
    trabalho_id TEXT, conceito_id TEXT, nome TEXT, nivel INTEGER, score REAL);
CREATE TABLE IF NOT EXISTS autores (
    id TEXT PRIMARY KEY, nome TEXT, instituicao_id TEXT, instituicao_nome TEXT, area_principal TEXT);
"""


def conectar():
    caminho = config.get("banco")
    os.makedirs(os.path.dirname(caminho) or ".", exist_ok=True)
    conn = sqlite3.connect(caminho)
    conn.executescript(ESQUEMA)
    return conn
