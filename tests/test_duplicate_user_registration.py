import pytest
from django.urls import reverse
from rest_framework import status


# test error while trying to register a duplicate user
@pytest.mark.django_db
def test_duplicate_user_registration(client):
    url = reverse('register')

    user_1 = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "password123",
        "is_employee": True,
    }

    user_2 = {
        "username": "testuser",
        "email": "testuser2@example.com",
        "password": "password123",
        "is_employee": True,
    }

    response_1 = client.post(url, user_1, format='json')
    response_2 = client.post(url, user_2, format='json')

    assert response_1.status_code == status.HTTP_201_CREATED
    assert response_2.status_code == status.HTTP_400_BAD_REQUEST

    assert 'username' in response_2.data
    assert response_2.data['username'][0] == "Username is already taken."
