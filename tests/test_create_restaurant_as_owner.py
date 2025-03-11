import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from api.models import Restaurant


# Test creating a restaurant as RestaurantOwner
@pytest.mark.django_db
def test_create_restaurant_as_owner(client):
    # RestaurantOwner creation
    user = get_user_model().objects.create_user(
        username='owner1',
        password='password123',
        email='owner1@example.com'
    )
    user.groups.add(Group.objects.get(name='RestaurantOwner'))

    # JWT login
    login_url = reverse('token_obtain_pair')
    login_data = {
        "username": "owner1",
        "password": "password123"
    }
    login_response = client.post(login_url, login_data, format='json')
    assert login_response.status_code == status.HTTP_200_OK
    token = login_response.data['access']

    # Restaurant creation
    url = reverse('restaurant-list')
    data = {
        "name": "Restaurant 1",
        "description": "Italian"
    }
    response = client.post(url, data, format='json', HTTP_AUTHORIZATION=f'Bearer {token}')

    assert response.status_code == status.HTTP_201_CREATED
    restaurant = Restaurant.objects.get(name='Restaurant 1')
    assert restaurant.name == "Restaurant 1"
    assert restaurant.description == "Italian"
    assert restaurant.owner == user
