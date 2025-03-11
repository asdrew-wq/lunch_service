import json
import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from api.models import Restaurant, Menu


@pytest.mark.django_db
def test_create_menu_version_2(client):
    # RestaurantOwner & Restaurant creation
    user = get_user_model().objects.create_user(
        username='owner1',
        password='password123',
        email='owner1@example.com'
    )
    user.groups.add(Group.objects.get(name='RestaurantOwner'))
    restaurant = Restaurant.objects.create(name='Restaurant 1', owner=user)

    # JWT login
    login_url = reverse('token_obtain_pair')
    login_data = {
        "username": "owner1",
        "password": "password123"
    }
    login_response = client.post(login_url, login_data, format='json')
    assert login_response.status_code == status.HTTP_200_OK
    token = login_response.data['access']

    # Menu creation for version 2.0
    url = reverse('menu-list')
    data = {
        "restaurant_id": restaurant.id,
        "content": json.dumps({"main": "Pizza Margherita"})
    }
    response = client.post(
        url,
        json.dumps(data),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {token}',
        HTTP_X_BUILD_VERSION='2.0'
    )

    assert response.status_code == status.HTTP_201_CREATED
    menu = Menu.objects.get(restaurant=restaurant)
    assert json.loads(menu.content) == {"main": "Pizza Margherita"}
    assert response.data['content'] == {"main": "Pizza Margherita"}
    assert 'items' not in response.data
