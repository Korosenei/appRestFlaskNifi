"""
Script de test automatisé pour l'API de réservation d'hôtel
Exécutez ce script après avoir lancé l'application Flask
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000"


class Colors:
    """Couleurs pour l'affichage console"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


def print_test(name, passed, message=""):
    """Affiche le résultat d'un test"""
    status = f"{Colors.GREEN}✓ PASS{Colors.END}" if passed else f"{Colors.RED}✗ FAIL{Colors.END}"
    print(f"{status} - {name}")
    if message:
        print(f"  {message}")


def test_home():
    """Test de la page d'accueil"""
    print(f"\n{Colors.BLUE}=== Test: Page d'accueil ==={Colors.END}")
    try:
        response = requests.get(f"{BASE_URL}/")
        passed = response.status_code == 200 and 'message' in response.json()
        print_test("GET /", passed, f"Status: {response.status_code}")
        return passed
    except Exception as e:
        print_test("GET /", False, str(e))
        return False


def test_get_stats():
    """Test des statistiques"""
    print(f"\n{Colors.BLUE}=== Test: Statistiques ==={Colors.END}")
    try:
        response = requests.get(f"{BASE_URL}/api/stats")
        data = response.json()
        passed = response.status_code == 200 and data['success']
        print_test("GET /api/stats", passed)
        if passed:
            print(f"  Clients: {data['data']['clients']}")
            print(f"  Chambres: {data['data']['chambres']['total']}")
            print(f"  Réservations: {data['data']['reservations']['total']}")
        return passed
    except Exception as e:
        print_test("GET /api/stats", False, str(e))
        return False


def test_clients():
    """Tests CRUD pour les clients"""
    print(f"\n{Colors.BLUE}=== Tests: Clients ==={Colors.END}")
    results = []

    # GET tous les clients
    try:
        response = requests.get(f"{BASE_URL}/api/clients")
        passed = response.status_code == 200
        print_test("GET /api/clients", passed)
        results.append(passed)
    except Exception as e:
        print_test("GET /api/clients", False, str(e))
        results.append(False)

    # POST créer un client
    try:
        new_client = {
            "nom": "Test",
            "prenom": "Utilisateur",
            "email": f"test.{datetime.now().timestamp()}@email.com",
            "telephone": "+33612345678"
        }
        response = requests.post(f"{BASE_URL}/api/clients", json=new_client)
        data = response.json()
        passed = response.status_code == 201 and data['success']
        print_test("POST /api/clients", passed)
        results.append(passed)

        if passed:
            client_id = data['data']['id']

            # GET client par ID
            response = requests.get(f"{BASE_URL}/api/clients/{client_id}")
            passed = response.status_code == 200
            print_test(f"GET /api/clients/{client_id}", passed)
            results.append(passed)

            # PUT mettre à jour
            update_data = {"telephone": "+33698765432"}
            response = requests.put(f"{BASE_URL}/api/clients/{client_id}", json=update_data)
            passed = response.status_code == 200
            print_test(f"PUT /api/clients/{client_id}", passed)
            results.append(passed)

            # DELETE supprimer
            response = requests.delete(f"{BASE_URL}/api/clients/{client_id}")
            passed = response.status_code == 200
            print_test(f"DELETE /api/clients/{client_id}", passed)
            results.append(passed)
    except Exception as e:
        print_test("POST /api/clients", False, str(e))
        results.append(False)

    return all(results)


def test_chambres():
    """Tests pour les chambres"""
    print(f"\n{Colors.BLUE}=== Tests: Chambres ==={Colors.END}")
    results = []

    # GET toutes les chambres
    try:
        response = requests.get(f"{BASE_URL}/api/chambres")
        passed = response.status_code == 200
        print_test("GET /api/chambres", passed)
        results.append(passed)
    except Exception as e:
        print_test("GET /api/chambres", False, str(e))
        results.append(False)

    # GET chambres disponibles
    try:
        response = requests.get(f"{BASE_URL}/api/chambres?disponible=true")
        passed = response.status_code == 200
        print_test("GET /api/chambres?disponible=true", passed)
        results.append(passed)
    except Exception as e:
        print_test("GET /api/chambres?disponible=true", False, str(e))
        results.append(False)

    # GET chambres par type
    try:
        response = requests.get(f"{BASE_URL}/api/chambres?type=Suite")
        passed = response.status_code == 200
        print_test("GET /api/chambres?type=Suite", passed)
        results.append(passed)
    except Exception as e:
        print_test("GET /api/chambres?type=Suite", False, str(e))
        results.append(False)

    return all(results)


def test_reservations():
    """Tests CRUD pour les réservations"""
    print(f"\n{Colors.BLUE}=== Tests: Réservations ==={Colors.END}")
    results = []

    # GET toutes les réservations
    try:
        response = requests.get(f"{BASE_URL}/api/reservations")
        passed = response.status_code == 200
        print_test("GET /api/reservations", passed)
        results.append(passed)
    except Exception as e:
        print_test("GET /api/reservations", False, str(e))
        results.append(False)

    # POST créer une réservation
    try:
        today = datetime.now()
        date_arrivee = (today + timedelta(days=30)).strftime('%Y-%m-%d')
        date_depart = (today + timedelta(days=35)).strftime('%Y-%m-%d')

        new_reservation = {
            "client_id": 1,
            "chambre_id": 1,
            "date_arrivee": date_arrivee,
            "date_depart": date_depart,
            "nombre_personnes": 1,
            "statut": "confirmee"
        }

        response = requests.post(f"{BASE_URL}/api/reservations", json=new_reservation)
        data = response.json()
        passed = response.status_code == 201 and data['success']
        print_test("POST /api/reservations", passed)
        results.append(passed)

        if passed:
            reservation_id = data['data']['id']

            # GET réservation par ID
            response = requests.get(f"{BASE_URL}/api/reservations/{reservation_id}")
            passed = response.status_code == 200
            print_test(f"GET /api/reservations/{reservation_id}", passed)
            results.append(passed)

            # PUT annuler réservation
            response = requests.put(f"{BASE_URL}/api/reservations/{reservation_id}/cancel")
            passed = response.status_code == 200
            print_test(f"PUT /api/reservations/{reservation_id}/cancel", passed)
            results.append(passed)

            # DELETE supprimer
            response = requests.delete(f"{BASE_URL}/api/reservations/{reservation_id}")
            passed = response.status_code == 200
            print_test(f"DELETE /api/reservations/{reservation_id}", passed)
            results.append(passed)
    except Exception as e:
        print_test("POST /api/reservations", False, str(e))
        results.append(False)

    return all(results)


def test_filters():
    """Tests des filtres"""
    print(f"\n{Colors.BLUE}=== Tests: Filtres ==={Colors.END}")
    results = []

    # Réservations par statut
    try:
        response = requests.get(f"{BASE_URL}/api/reservations?statut=confirmee")
        passed = response.status_code == 200
        print_test("GET /api/reservations?statut=confirmee", passed)
        results.append(passed)
    except Exception as e:
        print_test("GET /api/reservations?statut=confirmee", False, str(e))
        results.append(False)

    # Réservations par client
    try:
        response = requests.get(f"{BASE_URL}/api/reservations?client_id=1")
        passed = response.status_code == 200
        print_test("GET /api/reservations?client_id=1", passed)
        results.append(passed)
    except Exception as e:
        print_test("GET /api/reservations?client_id=1", False, str(e))
        results.append(False)

    return all(results)


def test_pagination():
    """Tests de la pagination"""
    print(f"\n{Colors.BLUE}=== Tests: Pagination ==={Colors.END}")
    results = []

    try:
        response = requests.get(f"{BASE_URL}/api/clients?page=1&per_page=2")
        data = response.json()
        passed = (response.status_code == 200 and
                  'pagination' in data and
                  data['pagination']['per_page'] == 2)
        print_test("GET /api/clients?page=1&per_page=2", passed)
        results.append(passed)
    except Exception as e:
        print_test("Pagination", False, str(e))
        results.append(False)

    return all(results)


def test_validation():
    """Tests de validation"""
    print(f"\n{Colors.BLUE}=== Tests: Validation ==={Colors.END}")
    results = []

    # Email invalide
    try:
        invalid_client = {
            "nom": "Test",
            "prenom": "Validation",
            "email": "email-invalide",
            "telephone": "+33612345678"
        }
        response = requests.post(f"{BASE_URL}/api/clients", json=invalid_client)
        passed = response.status_code == 400
        print_test("POST client avec email invalide (attendu: 400)", passed)
        results.append(passed)
    except Exception as e:
        print_test("Validation email", False, str(e))
        results.append(False)

    # Client inexistant
    try:
        response = requests.get(f"{BASE_URL}/api/clients/99999")
        passed = response.status_code == 404
        print_test("GET client inexistant (attendu: 404)", passed)
        results.append(passed)
    except Exception as e:
        print_test("Client inexistant", False, str(e))
        results.append(False)

    return all(results)


def main():
    """Fonction principale"""
    print(f"\n{Colors.YELLOW}{'=' * 60}")
    print(f"  Tests API Réservation Hôtel")
    print(f"  URL: {BASE_URL}")
    print(f"{'=' * 60}{Colors.END}\n")

    # Vérifier que l'API est accessible
    try:
        requests.get(f"{BASE_URL}/")
    except requests.exceptions.ConnectionError:
        print(f"{Colors.RED}ERREUR: Impossible de se connecter à {BASE_URL}")
        print(f"Assurez-vous que l'application Flask est en cours d'exécution.{Colors.END}")
        return

    # Exécuter tous les tests
    test_results = {
        "Page d'accueil": test_home(),
        "Statistiques": test_get_stats(),
        "Clients": test_clients(),
        "Chambres": test_chambres(),
        "Réservations": test_reservations(),
        "Filtres": test_filters(),
        "Pagination": test_pagination(),
        "Validation": test_validation()
    }

    # Résumé
    print(f"\n{Colors.YELLOW}{'=' * 60}")
    print(f"  Résumé des tests")
    print(f"{'=' * 60}{Colors.END}\n")

    total = len(test_results)
    passed = sum(1 for result in test_results.values() if result)

    for name, result in test_results.items():
        status = f"{Colors.GREEN}✓{Colors.END}" if result else f"{Colors.RED}✗{Colors.END}"
        print(f"{status} {name}")

    print(f"\n{Colors.YELLOW}Total: {passed}/{total} tests réussis{Colors.END}")

    if passed == total:
        print(f"{Colors.GREEN}🎉 Tous les tests sont passés avec succès!{Colors.END}\n")
    else:
        print(f"{Colors.RED}⚠️  Certains tests ont échoué.{Colors.END}\n")


if __name__ == "__main__":
    main()