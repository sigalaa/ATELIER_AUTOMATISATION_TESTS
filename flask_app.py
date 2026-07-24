from flask import Flask, render_template_string, render_template, jsonify, request, redirect, url_for, session
from flask import json
from urllib.request import urlopen
from werkzeug.utils import secure_filename
import sqlite3

# Importation de nos modules créés pour l'atelier
from tester.runner import execute_run
import storage

app = Flask(__name__)

# Initialisation de la base de données SQLite au démarrage
storage.init_db()

# --- VOTRE ROUTE D'ORIGINE (Conservée) ---
@app.get("/")
def consignes():
    return render_template('consignes.html')

# --- NOS NOUVELLES ROUTES (Dashboard & Tests) ---
@app.route('/health')
def health():
    """Bonus : Point de terminaison pour vérifier l'état de santé."""
    return jsonify({"status": "OK", "service": "Testing API Dashboard"})

@app.route('/run', methods=['GET'])
def trigger_run():
    """Déclenche manuellement un run de tests et le sauvegarde."""
    run_data = execute_run()
    storage.save_run(run_data)
    # Retourne le résultat en JSON (utilisé par le bouton du dashboard)
    return jsonify({"message": "Run effectué avec succès", "data": run_data})

@app.route('/dashboard')
def dashboard():
    """Affiche le tableau de bord HTML avec l'historique."""
    runs = storage.get_recent_runs(limit=20)
    return render_template('dashboard.html', runs=runs)

if __name__ == "__main__":
    # utile en local uniquement
    app.run(host="0.0.0.0", port=5000, debug=True)
