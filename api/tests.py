from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import *
from .serializers import *

""" Test Data Dictionary"""

test_data = {
            'email': 'test@example.com',
            'password': '1122',
            'username': 'testuser',
            'name': 'Test User',
            'team_name': 'Test Team',
            'team_country': 'Pakistan'
        }

"""Test for Custom User Model"""

class CustomUserModelTest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email=test_data['email'],
            password=test_data['password'],
            username=test_data['username'],
            name=test_data['name']
        )

    def test_create_user(self):
        self.assertEqual(self.user.email, test_data['email'])

"""Test for User Register Serializer"""

class UserRegisterSerializerTest(APITestCase):
    def setUp(self):
        self.serializer = UserRegisterSerializer(data=test_data.copy())

    def test_serializer_valid(self):
        is_valid = self.serializer.is_valid()
        if not is_valid:
            print(self.serializer.errors)
        self.assertTrue(is_valid)

"""Test for User Register View"""

class UserRegisterViewTest(APITestCase):
    def setUp(self):
        self.url = reverse('user-register')

    def test_user_register(self):
        response = self.client.post(self.url, test_data.copy(), format='json')
        if response.status_code != status.HTTP_201_CREATED:
            print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

"""Test for User Login Serializer"""

class UserLoginSerializerTest(APITestCase):
    def setUp(self):
        self.serializer = UserLoginSerializer(data={'email': test_data['email'], 'password': test_data['password']})

    def test_serializer_valid(self):
        is_valid = self.serializer.is_valid()
        if not is_valid:
            print(self.serializer.errors)
        self.assertTrue(is_valid)

"""Test for User Login View"""

class UserLoginViewTest(APITestCase):
    def setUp(self):
        self.url = reverse('user-login')
        self.user = CustomUser.objects.create_user(
            email=test_data['email'],
            password=test_data['password']
        )
        self.team = Team.objects.create(owner=self.user, 
                                        name=test_data['team_name'], 
                                        country=test_data['team_country']
                                    )
    def test_user_login(self):
        response = self.client.post(self.url, {'email': test_data['email'], 'password': test_data['password']}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data)
