import json
import pytest
from server import app, loadClubs, loadCompetitions


@pytest.fixture
def client():
    """
    Fixture to set up a test client for the Flask app
    """
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_integration_booking_flow(client):
    """
    Test d'intégration pour vérifier le flux de réservation.
    """
    # Charger l'état initial des clubs et compétitions
    clubs_data = loadClubs()
    competitions_data = loadCompetitions()

    initial_club = clubs_data[3]
    initial_competition = competitions_data[3]
    initial_points = int(initial_club['points'])
    initial_places = int(initial_competition['numberOfPlaces'])

    # Ajouter des logs pour mieux suivre le déroulement du test
    print(f"Avant réservation - Places disponibles: {initial_places}, Points du club: {initial_points}")

    # Simuler la connexion
    login_response = client.post('/showSummary', data={
        'email': initial_club['email']
    }, follow_redirects=True)
    assert login_response.status_code == 200
    assert b'Welcome' in login_response.data

    # Simuler la réservation de 3 places pour la compétition
    booking_response = client.post('/purchasePlaces', data={
        'competition': initial_competition['name'],
        'club': initial_club['name'],
        'places': 3
    }, follow_redirects=True)

    # Vérifier que la réservation a réussi
    assert booking_response.status_code == 200
    assert b'Great-booking complete!' in booking_response.data

    # Charger l'état mis à jour des clubs et compétitions
    updated_clubs_data = loadClubs()
    updated_competitions_data = loadCompetitions()

    # Vérifier que les points et les places ont été mis à jour
    updated_club = next(club for club in updated_clubs_data if club['name'] == initial_club['name'])
    updated_competition = next(comp for comp in updated_competitions_data if comp['name'] == initial_competition['name'])

    updated_points = int(updated_club['points'])
    updated_places = int(updated_competition['numberOfPlaces'])

    # Ajouter des logs pour suivre les changements après la réservation
    print(f"Après réservation - Places disponibles: {updated_places}, Points du club: {updated_points}")

    # Vérifications des résultats après la réservation
    assert updated_points == initial_points - 3, f"Erreur: points attendus: {initial_points - 3}, obtenus: {updated_points}"
    assert updated_places == initial_places - 3, f"Erreur: places attendues: {initial_places - 3}, obtenues: {updated_places}"