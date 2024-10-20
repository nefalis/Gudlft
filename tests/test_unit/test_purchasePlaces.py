import pytest
from server import app, clubs, competitions


@pytest.fixture
def client():
    """
    Fixture to set up a test client for the Flask app.
    """
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_reservation_success(client):
    """
    Test to check successful reservation.
    """
    club = clubs[3]
    competition = competitions[3]

    # Simulate a valid reservation by setting a future competition date.
    competition['date'] = "2025-01-01 10:00:00"
    response = client.post('/purchasePlaces', data={
        'competition': competition['name'],
        'club': club['name'],
        'places': 1
    })

    assert b'Great-booking complete!' in response.data


def test_reservation_insufficient_points(client):
    """
    Test to check reservation failure due to insufficient club points.
    """
    club = clubs[3]
    competition = competitions[3]

    # Set the club's points to a value less than the requested places.
    club['points'] = 1
    response = client.post('/purchasePlaces', data={
        'competition': competition['name'],
        'club': club['name'],
        'places': 5
    })
    assert b"You don't have enough points." in response.data


def test_reservation_insufficient_places(client):
    """
    Test to check reservation failure due to insufficient competition places.
    """
    club = clubs[3]
    competition = competitions[3]

    # Set the number of available places in the competition to 2.
    competition['numberOfPlaces'] = 2
    response = client.post('/purchasePlaces', data={
        'competition': competition['name'],
        'club': club['name'],
        'places': 3
    })
    assert b"Not enough places available." in response.data


def test_reservation_exceeding_limit(client):
    """
    Test to check reservation failure if the club requests more than 12 places.
    """
    club = clubs[3]
    competition = competitions[3]

    # Set the competition to have enough places.
    competition['numberOfPlaces'] = 20
    response = client.post('/purchasePlaces', data={
        'competition': competition['name'],
        'club': club['name'],
        'places': 15
    })
    assert b"You cannot book more than 12 places per competition." in response.data


def test_booking_past_competition(client):
    """
    Test to check booking failure for a competition that has already ended.
    """
    club = clubs[3]
    competition = competitions[3]

    # Set the competition date to a past date.
    competition['date'] = "2000-01-01 10:00:00"
    response = client.post('/purchasePlaces', data={
        'competition': competition['name'],
        'club': club['name'],
        'places': 1
    }, follow_redirects=True)

    assert b"You cannot book places for a competition that has already ended." in response.data
