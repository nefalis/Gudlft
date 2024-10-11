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
    Integration test to verify the booking flow.
    """
    clubs_data = loadClubs()
    competitions_data = loadCompetitions()

    initial_club = clubs_data[3]
    initial_competition = competitions_data[3]
    initial_points = int(initial_club['points'])
    initial_places = int(initial_competition['numberOfPlaces'])

    # Simulate the login
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

    # Verify that the booking was successful
    assert booking_response.status_code == 200
    assert b'Great-booking complete!' in booking_response.data

    # Load the updated state of the clubs and competitions
    updated_clubs_data = loadClubs()
    updated_competitions_data = loadCompetitions()

    # Verify that the points and places have been updated
    updated_club = next(club for club in updated_clubs_data if club['name'] == initial_club['name'])
    updated_competition = next(
        comp for comp in updated_competitions_data if comp['name'] == initial_competition['name']
        )

    updated_points = int(updated_club['points'])
    updated_places = int(updated_competition['numberOfPlaces'])

    # Check the results after booking
    assert updated_points == initial_points - 3, (
        f"Erreur: points attendus: {initial_points - 3}, obtenus: {updated_points}"
        )
    assert updated_places == initial_places - 3, (
        f"Erreur: places attendues: {initial_places - 3}, obtenues: {updated_places}"
        )
