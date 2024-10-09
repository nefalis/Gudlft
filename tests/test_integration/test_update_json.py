import json
import pytest
from server import app


@pytest.fixture
def client():
    """
    Fixture to set up a test client for the Flask app
    """
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_update_json(client):
    """
    Test to check that the JSON file is updated after a successful booking
    """
    with open('clubs.json') as f:
        clubs_data = json.load(f)

    initial_club = clubs_data['clubs'][0]
    initial_points = int(initial_club['points'])

    # Simulate booking 2 places for a competition
    response = client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',
        'club': initial_club['name'],
        'places': 2
    }, follow_redirects=True)

    # Load the updated state of the clubs after the booking
    with open('clubs.json') as f:
        updated_clubs_data = json.load(f)

    # Verify that the club's points have been correctly updated 
    updated_points = int(updated_clubs_data['clubs'][0]['points'])
    assert updated_points == initial_points - 2

    assert b'Great-booking complete!' in response.data


if __name__ == '__main__':
    pytest.main()
