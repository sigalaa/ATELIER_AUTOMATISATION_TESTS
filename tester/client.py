import requests
import time

class ApiClient:
    def __init__(self, base_url="https://api.agify.io", timeout=3.0, max_retries=1):
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries

    def get(self, endpoint="", params=None):
        """
        Exécute une requête GET avec gestion des timeouts, retrys et mesure de latence.
        Retourne un dictionnaire standardisé utilisable par les tests.
        """
        url = f"{self.base_url}{endpoint}"
        attempts = 0
        
        while attempts <= self.max_retries:
            attempts += 1
            start_time = time.time()
            
            try:
                # On lance la requête avec le timeout imposé
                response = requests.get(url, params=params, timeout=self.timeout)
                
                # Calcul de la latence en millisecondes
                latency_ms = int((time.time() - start_time) * 1000)
                
                # Gestion du Rate Limiting (429) ou Erreur Serveur (5xx)
                if response.status_code in [429, 500, 502, 503, 504]:
                    if attempts <= self.max_retries:
                        # Backoff simple : on attend 2 secondes avant de réessayer
                        time.sleep(2)
                        continue
                
                # Si on arrive ici, c'est que la requête a abouti (même si c'est une 404 ou 422 attendue)
                try:
                    json_data = response.json()
                except ValueError:
                    json_data = None

                return {
                    "success": True,
                    "status_code": response.status_code,
                    "json": json_data,
                    "latency_ms": latency_ms,
                    "error": None,
                    "attempts": attempts
                }

            except requests.exceptions.Timeout:
                # Timeout atteint (ex: > 3s)
                if attempts <= self.max_retries:
                    time.sleep(1) # Petite pause avant de retenter
                    continue
                return self._error_response("Timeout dépassé", start_time, attempts)
                
            except requests.exceptions.RequestException as e:
                # Autre erreur réseau (DNS, coupure internet...)
                if attempts <= self.max_retries:
                    time.sleep(1)
                    continue
                return self._error_response(f"Erreur réseau: {str(e)}", start_time, attempts)

    def _error_response(self, message, start_time, attempts):
        """Formate une réponse d'erreur en cas d'échec total (après tous les retrys)"""
        latency_ms = int((time.time() - start_time) * 1000)
        return {
            "success": False,
            "status_code": None,
            "json": None,
            "latency_ms": latency_ms,
            "error": message,
            "attempts": attempts
        }
