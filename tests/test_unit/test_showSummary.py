import pytest
from server import app


@pytest.fixture
def test_client():
    """
    Fixture to set up a test client for the Flask app.
    """
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_valid_mail(test_client):
    """
    Test to check the behavior with a valid email.
    """
    data = {'email': 'admin@irontemple.com'}
    response = test_client.post('/showSummary', data=data)
    assert response.status_code == 200


def test_invalid_mail(test_client):
    """
    Test to check the behavior with an invalid email.
    """
    data = {'email': 'novalid@mail.com'}
    response = test_client.post('/showSummary', data=data)
    assert response.status_code == 302

    # Follow the redirection to the homepage.
    follow_response = test_client.get(response.location)

    assert b"Sorry, that email wasn't found." in follow_response.data
