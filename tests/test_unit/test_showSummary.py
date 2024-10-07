import pytest
from server import app

@pytest.fixture
def test_client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_valid_mail(test_client):
    data = {'email': 'admin@irontemple.com'}
    response = test_client.post('/showSummary', data=data)
    assert response.status_code == 200

def test_invalid_mail(test_client):
    data = {'email': 'novalid@mail.com'}
    response = test_client.post('/showSummary', data=data)
    assert response.status_code == 302

    # Suit la redirection vers la page d'accueil
    follow_response = test_client.get(response.location)

    # Vérifiez le message flash sur la page d'accueil en tenant compte de l'entité HTML
    assert b"Sorry, that email wasn't found." in follow_response.data