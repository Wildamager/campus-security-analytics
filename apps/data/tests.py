from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from apps.camerastream.models import Camers, EntryCarLog, EntryPersonLog
from .models import Car, Person


class ApiAuthTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='tester', password='Str0ngTestPass!'
        )

    def test_token_obtain_returns_pair(self):
        response = self.client.post(
            '/api/auth/token/',
            {'username': 'tester', 'password': 'Str0ngTestPass!'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_anonymous_access_is_rejected(self):
        self.assertEqual(
            self.client.get('/api/persons/').status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_bearer_token_grants_access(self):
        token = self._access_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual(
            self.client.get('/api/persons/').status_code,
            status.HTTP_200_OK,
        )

    def _access_token(self):
        response = self.client.post(
            '/api/auth/token/',
            {'username': 'tester', 'password': 'Str0ngTestPass!'},
            format='json',
        )
        return response.data['access']


class PersonApiTests(APITestCase):
    def setUp(self):
        User.objects.create_user(username='tester', password='Str0ngTestPass!')
        token = self.client.post(
            '/api/auth/token/',
            {'username': 'tester', 'password': 'Str0ngTestPass!'},
            format='json',
        ).data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        self.person = Person.objects.create(
            name='Ivan Petrov', email='Ivan.Petrov@Example.com ', contact='+79990000000'
        )

    def test_list_is_paginated(self):
        response = self.client.get('/api/persons/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(response.data['count'], 1)

    def test_create_person(self):
        response = self.client.post(
            '/api/persons/',
            {'name': 'Anna Ivanova', 'email': 'anna@example.com', 'contact': '+79991111111'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Person.objects.count(), 2)

    def test_email_is_normalised(self):
        response = self.client.patch(
            f'/api/persons/{self.person.id}/', {'email': 'NEW@Example.COM'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.person.refresh_from_db()
        self.assertEqual(self.person.email, 'new@example.com')

    def test_search_filters_results(self):
        response = self.client.get('/api/persons/?search=ivan')
        self.assertEqual(response.data['count'], 1)
        response = self.client.get('/api/persons/?search=nobody')
        self.assertEqual(response.data['count'], 0)

    def test_put_is_not_allowed(self):
        response = self.client.put(
            f'/api/persons/{self.person.id}/', {'name': 'x'}, format='json'
        )
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_delete_person(self):
        response = self.client.delete(f'/api/persons/{self.person.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Person.objects.filter(id=self.person.id).exists())


class CarApiTests(APITestCase):
    def setUp(self):
        User.objects.create_user(username='tester', password='Str0ngTestPass!')
        token = self.client.post(
            '/api/auth/token/',
            {'username': 'tester', 'password': 'Str0ngTestPass!'},
            format='json',
        ).data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_plate_is_normalised(self):
        response = self.client.post(
            '/api/cars/',
            {'owner': 'Sergey M.', 'number': ' а 123 вс 777 ', 'brand': 'Lada'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['number'], 'А123ВС777')

    def test_search_by_owner(self):
        Car.objects.create(owner='Sergey M.', number='A123BC777', brand='Lada')
        response = self.client.get('/api/cars/?search=sergey')
        self.assertEqual(response.data['count'], 1)


class CameraApiTests(APITestCase):
    def setUp(self):
        User.objects.create_user(username='tester', password='Str0ngTestPass!')
        token = self.client.post(
            '/api/auth/token/',
            {'username': 'tester', 'password': 'Str0ngTestPass!'},
            format='json',
        ).data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_credentials_are_write_only(self):
        response = self.client.post(
            '/api/cameras/',
            {
                'location': 'Main entrance',
                'ip': '192.168.1.10',
                'port': 8000,
                'login': 'admin',
                'password': 'secret',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('password', response.data)
        self.assertNotIn('login', response.data)
        self.assertTrue(response.data['has_credentials'])

        listed = self.client.get('/api/cameras/').data['results'][0]
        self.assertNotIn('password', listed)

    def test_logs_are_read_only(self):
        EntryPersonLog.objects.create(name='Ivan Petrov', location='Gate')
        EntryCarLog.objects.create(number='A123BC777', location='Gate')

        response = self.client.get('/api/logs/persons/')
        self.assertEqual(response.data['count'], 1)
        response = self.client.get('/api/logs/cars/')
        self.assertEqual(response.data['count'], 1)

        response = self.client.post(
            '/api/logs/persons/', {'name': 'X', 'location': 'Y'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class SummaryApiTests(APITestCase):
    def setUp(self):
        User.objects.create_user(username='tester', password='Str0ngTestPass!')
        token = self.client.post(
            '/api/auth/token/',
            {'username': 'tester', 'password': 'Str0ngTestPass!'},
            format='json',
        ).data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_summary_counts(self):
        Person.objects.create(name='Ivan Petrov', email='i@example.com', contact='')
        Car.objects.create(owner='Sergey M.', number='A123BC777', brand='Lada')
        Camers.objects.create(location='Gate', ip='192.168.1.10', port=8000)
        EntryPersonLog.objects.create(name='Ivan Petrov', location='Gate')

        response = self.client.get('/api/summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'cameras': 1,
            'persons': 1,
            'cars': 1,
            'person_entries': 1,
            'car_entries': 0,
        })