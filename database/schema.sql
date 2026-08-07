PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS domains (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL UNIQUE,

    domain TEXT NOT NULL UNIQUE,

    api_key TEXT,

    sitemap TEXT,

    active INTEGER DEFAULT 1,

    created_at TEXT NOT NULL,

    updated_at TEXT

);

CREATE TABLE IF NOT EXISTS urls (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    domain_id INTEGER NOT NULL,

    url TEXT NOT NULL,

    status TEXT DEFAULT 'PENDIENTE',

    response_code INTEGER,

    response_message TEXT,

    retries INTEGER DEFAULT 0,

    submitted_at TEXT,

    indexed_at TEXT,

    FOREIGN KEY(domain_id)
    REFERENCES domains(id)
);

CREATE TABLE IF NOT EXISTS history (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    event_date TEXT,

    event_type TEXT,

    description TEXT

);

CREATE TABLE IF NOT EXISTS settings (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    key TEXT UNIQUE,

    value TEXT
);