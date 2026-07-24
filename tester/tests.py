from .client import ApiClient

def run_tests():
    """
    Exécute la suite de tests sur l'API Agify.
    Retourne une liste de résultats de tests sous forme de dictionnaires.
    """
    client = ApiClient()
    results = []
    
    # ---------------------------------------------------------
    # SCÉNARIO 1 : Requête valide (Cas nominal)
    # ---------------------------------------------------------
    resp_valid = client.get(params={"name": "lucas"})
    latency = resp_valid.get("latency_ms", 0)
    json_data = resp_valid.get("json")
    
    # Test 1 : Disponibilité (Code HTTP 200 attendu)
    if resp_valid["success"] and resp_valid["status_code"] == 200:
        results.append({"name": "HTTP 200 (Nominal)", "status": "PASS", "latency_ms": latency})
    else:
        results.append({"name": "HTTP 200 (Nominal)", "status": "FAIL", "latency_ms": latency, "details": f"Code HTTP inattendu : {resp_valid.get('status_code')}"})

    # Test 2 : Format (Le corps de la réponse doit être un JSON)
    if json_data is not None:
        results.append({"name": "Format JSON", "status": "PASS", "latency_ms": latency})
    else:
        results.append({"name": "Format JSON", "status": "FAIL", "latency_ms": latency, "details": "La réponse n'est pas un JSON valide"})

    # Test 3 : Contrat (Présence des champs obligatoires)
    has_fields = False
    if json_data:
        has_fields = all(key in json_data for key in ["count", "name", "age"])
        if has_fields:
            results.append({"name": "Champs obligatoires", "status": "PASS", "latency_ms": latency})
        else:
            results.append({"name": "Champs obligatoires", "status": "FAIL", "latency_ms": latency, "details": "Champs 'count', 'name' ou 'age' manquants"})
    
    # Test 4 : Types de données (Validité du schéma)
    if json_data and has_fields:
        # 'count' doit être un entier, 'name' une chaîne, 'age' un entier (ou None/null)
        type_ok = isinstance(json_data["count"], int) and isinstance(json_data["name"], str) and (isinstance(json_data["age"], int) or json_data["age"] is None)
        if type_ok:
            results.append({"name": "Types des données", "status": "PASS", "latency_ms": latency})
        else:
            results.append({"name": "Types des données", "status": "FAIL", "latency_ms": latency, "details": "Erreur de typage (ex: age n'est pas un entier)"})

    # Test 5 : QoS (La latence doit être inférieure à 1000ms)
    if latency < 1000:
        results.append({"name": "Latence acceptable (< 1s)", "status": "PASS", "latency_ms": latency})
    else:
        results.append({"name": "Latence acceptable (< 1s)", "status": "FAIL", "latency_ms": latency, "details": f"Latence trop élevée ({latency}ms)"})

    # ---------------------------------------------------------
    # SCÉNARIO 2 : Requête invalide (Test de robustesse)
    # ---------------------------------------------------------
    # On omet volontairement le paramètre "name" qui est obligatoire
    resp_invalid = client.get() 
    lat_inv = resp_invalid.get("latency_ms", 0)

    # Test 6 : Gestion des erreurs client (Code HTTP 422 attendu)
    if resp_invalid["status_code"] == 422:
        results.append({"name": "Code 422 (Erreur paramètre)", "status": "PASS", "latency_ms": lat_inv})
    else:
        results.append({"name": "Code 422 (Erreur paramètre)", "status": "FAIL", "latency_ms": lat_inv, "details": f"Attendu 422, reçu {resp_invalid.get('status_code')}"})

    return results
