from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
EXISTING_USER_URL = reverse('user:me')

def create_user(**params):
    return get_user_model().objects.create_user(**params)

class PublicUserApiTest(TestCase):
    # tests for public user how are visiting
    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        #To test the user with valid paylosd is success
        payload = {
            'email':'test@gmail.com',
            'password': 'test123',
            'name': 'test'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        #testing that usercredentials are correct 
        payload = {
            'email':'test@gmail.com',
            'password': 'test123'
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_is_tooshort(self):
        #Checking that the password is grater than 5 charecter
        payload = {
            'email':'test@gmail.com',
            'password': 'test'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        payload = {
            'email':'test@gmail.com',
            'password':'test123'
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_taken_for_invalid_credintials(self):
        create = {
            'email':'test@gmail.com',
            'password':'test123'
        }
        create_user(**create)
        payload = {
            'email':'test@gmail.com',
            'password':'test12'
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        payload = {
            'email':'test@gmail.com',
            'password':'test123'
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


    def test_create_token_missing_field(self):
        payload = {
            'email':'test@gmail.com',
            'password':''
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrive_user_unauthorized(self):
        res = self.client.get(EXISTING_USER_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivetUserApiTests(TestCase):
    
    def setUp(self):
        self.user = create_user(
            email = 'email@gmail.com',
            password = 'password',
            name = 'name'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        res = self.client.get(EXISTING_USER_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            "email" : self.user.email,
            "name" : self.user.name
        })

    def test_post_not_allow(self):

        res = self.client.post(EXISTING_USER_URL)
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        payload = {
            'name' : 'newname',
            'password' : 'newpass'
        }
        res = self.client.patch(EXISTING_USER_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password, payload['password'])
        self.assertEqual(res.status_code, status.HTTP_200_OK)