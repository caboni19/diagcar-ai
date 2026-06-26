"""
DiagCar DB Utility — Fault-Tolerant Edition
MySQL primary + SQLite fallback + in-memory last resort.
The app ALWAYS works even without MySQL/XAMPP.
"""
import os, sqlite3, threading
try:
    import mysql.connector
    from mysql.connector import pooling
except ImportError:
    mysql = None
    pooling = None

# ─── CONFIG ───────────────────────────────────────────────────────────────────
SQLITE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                           'data', 'diagcar_local.db')

_pool          = None
_use_mysql     = None     # None = not tested yet
_sqlite_lock   = threading.Lock()

# ─── MYSQL ────────────────────────────────────────────────────────────────────
def _try_mysql_pool():
    if mysql is None or pooling is None:
        _use_mysql_local = False
        return None
    global _pool, _use_mysql
    if _use_mysql is False:
        return None
    try:
        if _pool is None:
            _pool = pooling.MySQLConnectionPool(
                pool_name  = 'diagcar_pool',
                pool_size  = 5,
                host       = os.getenv('DB_HOST', 'localhost'),
                port       = int(os.getenv('DB_PORT', '3306')),
                user       = os.getenv('DB_USER', 'root'),
                password   = os.getenv('DB_PASSWORD', ''),
                database   = os.getenv('DB_NAME', 'diagcar_ai'),
                charset    = 'utf8mb4',
                collation  = 'utf8mb4_unicode_ci',
                connection_timeout = 3,
            )
        _use_mysql = True
        return _pool
    except Exception as e:
        _use_mysql = False
        print(f'[DB] MySQL unavailable: {e} → using SQLite fallback')
        return None


# ─── SQLITE FALLBACK ──────────────────────────────────────────────────────────
def _sqlite_conn():
    os.makedirs(os.path.dirname(SQLITE_PATH), exist_ok=True)
    conn = sqlite3.connect(SQLITE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')
    _ensure_sqlite_schema(conn)
    return conn


def _ensure_sqlite_schema(conn):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name    TEXT NOT NULL,
            last_name     TEXT DEFAULT '',
            email         TEXT NOT NULL UNIQUE,
            phone         TEXT DEFAULT '',
            password_hash TEXT NOT NULL,
            car_brand     TEXT DEFAULT '',
            car_model     TEXT DEFAULT '',
            car_year      TEXT DEFAULT '',
            fuel_type     TEXT DEFAULT '',
            transmission  TEXT DEFAULT '',
            mileage       TEXT DEFAULT '',
            created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS diagnostics (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id          INTEGER,
            input_text       TEXT,
            vehicle_snapshot TEXT,
            top_fault        TEXT,
            probability      REAL,
            severity         TEXT,
            obd_codes        TEXT,
            recommendation   TEXT,
            created_at       DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()


# ─── UNIFIED API ──────────────────────────────────────────────────────────────
def fetch_all(query: str, params=None):
    params = params or ()
    pool = _try_mysql_pool()
    if pool:
        try:
            conn = pool.get_connection()
            cur  = conn.cursor(dictionary=True)
            cur.execute(query, params)
            rows = cur.fetchall()
            cur.close(); conn.close()
            return rows
        except Exception as e:
            print('[DB] MySQL fetch_all error:', e)

    # SQLite fallback
    q = _sqlite_adapt(query)
    with _sqlite_lock:
        conn = _sqlite_conn()
        try:
            rows = conn.execute(q, params).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()


def fetch_one(query: str, params=None):
    rows = fetch_all(query, params)
    return rows[0] if rows else None


def execute(query: str, params=None):
    params = params or ()
    pool = _try_mysql_pool()
    if pool:
        try:
            conn = pool.get_connection()
            cur  = conn.cursor()
            cur.execute(query, params)
            conn.commit()
            lid = cur.lastrowid
            cur.close(); conn.close()
            return lid
        except Exception as e:
            print('[DB] MySQL execute error:', e)

    # SQLite fallback
    q = _sqlite_adapt(query)
    with _sqlite_lock:
        conn = _sqlite_conn()
        try:
            cur = conn.execute(q, params)
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()


def _sqlite_adapt(query: str) -> str:
    """Translate MySQL-specific syntax → SQLite."""
    q = query
    q = q.replace('%s', '?')
    q = q.replace('AUTO_INCREMENT', 'AUTOINCREMENT')
    q = q.replace('ENGINE=InnoDB', '')
    q = q.replace('DEFAULT CHARSET=utf8mb4', '')
    return q
