import sqlite3

db = sqlite3.connect("blackjack.db")
db.execute(
    "CREATE TABLE IF NOT EXISTS spelers ("
    "user_id INTEGER PRIMARY KEY, "
    "naam TEXT NOT NULL, "
    "saldo INTEGER NOT NULL DEFAULT 100)"
)
db.commit()

def maak_speler(user_id, naam):
    """Geeft True terug als de speler nieuw is."""
    cursor = db.execute(
        "INSERT OR IGNORE INTO spelers (user_id, naam, saldo) VALUES (?, ?, 100)",
        (user_id, naam),
    )
    db.commit()
    return cursor.rowcount == 1

def bestaat(user_id):
    return db.execute("SELECT 1 FROM spelers WHERE user_id = ?", (user_id,)).fetchone() is not None

def get_saldo(user_id):
    rij = db.execute("SELECT saldo FROM spelers WHERE user_id = ?", (user_id,)).fetchone()
    return rij[0] if rij else None

def pas_saldo_aan(user_id, verschil):
    db.execute("UPDATE spelers SET saldo = saldo + ? WHERE user_id = ?", (verschil, user_id))
    db.commit()

def zet_saldo(user_id, saldo):
    db.execute("UPDATE spelers SET saldo = ? WHERE user_id = ?", (saldo, user_id))
    db.commit()

def verwijder_speler(user_id):
    db.execute("DELETE FROM spelers WHERE user_id = ?", (user_id,))
    db.commit()