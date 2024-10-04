import pytest
from server import app, clubs, competitions

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_reservation_success(client):
    club = clubs[0]
    competition = competitions[0]

    # Simuler une réservation valide
    response = client.post('/purchasePlaces', data={
        'competition': competition['name'],
        'club': club['name'],
        'places': 1
    })

    assert b'Great-booking complete!' in response.data


def test_reservation_insufficient_points(client):
    # Préparer les données avec un club n'ayant pas assez de points
    club = clubs[0]
    competition = competitions[0]
    
    # Simuler une tentative de réservation où le club n'a pas assez de points
    club['points'] = 1
    response = client.post('/purchasePlaces', data={
        'competition': competition['name'],
        'club': club['name'],
        'places': 5
    })
    assert b"You don't have enough points." in response.data


def test_reservation_insufficient_places(client):
    # Préparer les données avec une compétition n'ayant pas assez de places
    club = clubs[0]
    competition = competitions[0]

    # Simuler une tentative de réservation où il n'y a pas assez de places
    competition['numberOfPlaces'] = 2
    response = client.post('/purchasePlaces', data={
        'competition': competition['name'],
        'club': club['name'],
        'places': 3
    })
    assert b"Not enough places available." in response.data

def test_reservation_exceeding_limit(client):
    # Test si on tente de réserver plus de 12 places
    club = clubs[0]
    competition = competitions[0]

    # Simuler une tentative de réservation avec plus de 12 places
    competition['numberOfPlaces'] = 20
    response = client.post('/purchasePlaces', data={
        'competition': competition['name'],
        'club': club['name'],
        'places': 15
    })
    assert b"You cannot book more than 12 places per competition." in response.data