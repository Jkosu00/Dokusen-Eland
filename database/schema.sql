DROP TABLE IF EXISTS partidas;
DROP TABLE IF EXISTS jugadores;
DROP TABLE IF EXISTS propiedades;
DROP TABLE IF EXISTS calculos_lagrange;
DROP TABLE IF EXISTS transacciones;
DROP TABLE IF EXISTS eventos;
DROP TABLE IF EXISTS mejora_yonkou;

CREATE TABLE partidas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    cantidad_jugadores INTEGER,
    ganador TEXT,
    condicion_victoria TEXT
);

CREATE TABLE jugadores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    partida_id INTEGER,
    nombre TEXT NOT NULL,
    berries REAL DEFAULT 1500,
    riqueza_total REAL DEFAULT 0,
    monopolios INTEGER DEFAULT 0,
    road_poneglyphs INTEGER DEFAULT 0,

    FOREIGN KEY (partida_id)
        REFERENCES partidas(id)
);

CREATE TABLE propiedades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    partida_id INTEGER,
    nombre TEXT NOT NULL,
    tipo TEXT NOT NULL,
    grupo_color TEXT,
    propietario TEXT,
    nivel_mejora INTEGER DEFAULT 0,
    precio_actual REAL,

    FOREIGN KEY (partida_id)
        REFERENCES partidas(id)
);

CREATE TABLE calculos_lagrange (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    partida_id INTEGER,

    turno INTEGER,
    propiedad TEXT,

    puntos_usados INTEGER,
    x_eval REAL,

    precio_estimado REAL,
    precio_real REAL,

    error_absoluto REAL,
    error_porcentual REAL,

    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (partida_id)
        REFERENCES partidas(id)
);

CREATE TABLE transacciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    partida_id INTEGER,
    turno INTEGER,

    jugador TEXT,
    tipo TEXT,

    monto REAL,

    propiedad TEXT,

    descripcion TEXT,

    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (partida_id)
        REFERENCES partidas(id)
);

CREATE TABLE eventos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    partida_id INTEGER,
    turno INTEGER,

    jugador TEXT,

    tipo_evento TEXT,
    efecto TEXT,

    monto REAL,

    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (partida_id)
        REFERENCES partidas(id)
);

CREATE TABLE mejora_yonkou (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    partida_id INTEGER,
    turno INTEGER,

    jugador_yonkou TEXT,

    isla_mejorada TEXT,

    jugador_anterior TEXT,

    isla_anterior TEXT,

    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (partida_id)
        REFERENCES partidas(id)
);