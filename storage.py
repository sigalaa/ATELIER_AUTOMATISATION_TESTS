import sqlite3
import json
from datetime import datetime

DB_PATH = "runs.db"

def init_db():
    """Crée la table si elle n'existe pas encore."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # On stocke les métriques principales en colonnes pour faciliter l'affichage,
    # et le détail complet des tests dans la colonne raw_data (format JSON).
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            passed INTEGER,
            failed INTEGER,
            error_rate REAL,
            latency_avg REAL,
            latency_p95 REAL,
            raw_data TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_run(run_data):
    """Sauvegarde les résultats d'une exécution de tests (un 'run')."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    summary = run_data.get("summary", {})
    
    cursor.execute('''
        INSERT INTO runs (timestamp, passed, failed, error_rate, latency_avg, latency_p95, raw_data)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        run_data.get("timestamp", datetime.now().isoformat()),
        summary.get("passed", 0),
        summary.get("failed", 0),
        summary.get("error_rate", 0.0),
        summary.get("latency_ms_avg", 0),
        summary.get("latency_ms_p95", 0),
        json.dumps(run_data)  # On convertit le dictionnaire Python en texte JSON
    ))
    
    conn.commit()
    conn.close()

def get_recent_runs(limit=20):
    """Récupère les derniers runs pour les afficher dans le dashboard."""
    conn = sqlite3.connect(DB_PATH)
    # Permet de récupérer les lignes sous forme de dictionnaires plutôt que de simples tuples
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    
    # On trie par ID décroissant pour avoir les plus récents en premier
    cursor.execute('SELECT * FROM runs ORDER BY id DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    # Convertit les lignes SQLite en vrais dictionnaires Python
    return [dict(row) for row in rows]
