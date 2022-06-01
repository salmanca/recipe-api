from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENT_URL = reverse('recipe:ingredient-list')

class PublicIngredientApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivetIngredientApiTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email = 'test@gmail.com',
            password = 'test123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrive_ingredient(self):
        Ingredient.objects.create(user = self.user, name = 'Kale')
        Ingredient.objects.create(user = self.user, name = 'Salt')
        
        res = self.client.get(INGREDIENT_URL)
        tags = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(tags, many=True)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_user(self):
        user2 = get_user_model().objects.create_user(
            email = 'test1@gmail.com',
            password = 'test123'
        )
        Ingredient.objects.create(user = user2, name = 'Biriyani')
        tag = Ingredient.objects.create(user = self.user, name = 'Vegan')
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        payload = {
            'name' : 'testtag',
        }
        res = self.client.post(INGREDIENT_URL, payload)

        tag = Ingredient.objects.filter(user=self.user, name=payload['name']).exists()
        self.assertTrue(tag)

    def test_create_tag_invalid(self):
        payload = {'name' : ''}
        res = self.client.post(INGREDIENT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)