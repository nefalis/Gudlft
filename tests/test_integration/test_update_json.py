import json
import pytest
from flask import Flask
from server import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_update_json(client):
    with open('clubs.json') as f:
        clubs_data = json.load(f)

    initial_club = clubs_data['clubs'][0]
    initial_points = int(initial_club['points'])

    # Réserver 2 places dans une compétition
    response = client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',
        'club': initial_club['name'],
        'places': 2
    }, follow_redirects=True)

    # Charger l'état mis à jour des clubs
    with open('clubs.json') as f:
        updated_clubs_data = json.load(f)

    # Vérifiez que les points ont été correctement mis à jour
    updated_points = int(updated_clubs_data['clubs'][0]['points'])
    assert updated_points == initial_points - 2

    # Vérifiez que la réservation a réussi
    assert b'Great-booking complete!' in response.data


if __name__ == '__main__':
    pytest.main()