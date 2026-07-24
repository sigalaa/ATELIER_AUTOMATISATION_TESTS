import datetime
from .tests import run_tests

def calculate_p95(latencies):
    """
    Calcule le 95ème percentile d'une liste de latences.
    Le p95 indique que 95% des requêtes sont plus rapides que cette valeur.
    """
    if not latencies:
        return 0
    
    sorted_latencies = sorted(latencies)
    index = int(len(sorted_latencies) * 0.95)
    
    # Sécurité pour ne pas dépasser la taille de la liste
    if index >= len(sorted_latencies):
        index = len(sorted_latencies) - 1
        
    return sorted_latencies[index]

def execute_run():
    """
    Lance une campagne de tests, compile les métriques et formate le résultat final.
    """
    # 1. On lance les tests (le contrôleur qualité)
    test_results = run_tests()
    
    # 2. On initialise nos compteurs
    passed = 0
    failed = 0
    latencies = []
    
    # 3. On analyse chaque test individuellement
    for result in test_results:
        if result["status"] == "PASS":
            passed += 1
        else:
            failed += 1
            
        if "latency_ms" in result:
            latencies.append(result["latency_ms"])
            
    # 4. Calcul des métriques globales
    total_tests = passed + failed
    error_rate = round(failed / total_tests, 3) if total_tests > 0 else 0.0
    
    latency_avg = int(sum(latencies) / len(latencies)) if latencies else 0
    latency_p95 = calculate_p95(latencies)
    
    # 5. Formatage du rapport final selon le modèle attendu
    # Utilise le fuseau horaire local (astimezone)
    timestamp_now = datetime.datetime.now().astimezone().isoformat()
    
    run_data = {
        "api": "Agify",
        "timestamp": timestamp_now,
        "summary": {
            "passed": passed,
            "failed": failed,
            "error_rate": error_rate,
            "latency_ms_avg": latency_avg,
            "latency_ms_p95": latency_p95
        },
        "tests": test_results
    }
    
    return run_data
