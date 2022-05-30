from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Tag
from recipe.serializers import TagSerializer

TAG_URL = reverse('recipe:tag-list')

class PublicApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivetApiTests(TestCase):
    def setUp(self):
        email = 'test@gmail.com'
        password = 'test123'
        self.user = get_user_model().objects.create_user(
            email,
            password
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrive_tags(self):
        Tag.objects.create(user = self.user, name = 'Vegan')
        Tag.objects.create(user = self.user, name = 'Desert')
        
        res = self.client.get(TAG_URL)
        tags = Tag.objects.all().order_by('name')
        serializer = TagSerializer(tags, many=True)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_user(self):
        user2 = get_user_model().objects.create_user(
            email = 'test1@gmail.com',
            password = 'test123'
        )
        Tag.objects.create(user = user2, name = 'Biriyani')
        tag = Tag.objects.create(user = self.user, name = 'Vegan')
        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        payload = {
            'name' : 'test tag',
        }
        res = self.client.post(TAG_URL, payload)

        tag = Tag.objects.filter(user=self.user, name=payload['name']).exists()
        self.assertTrue(tag)

    def test_create_tag_invalid(self):
        payload = {'name' : ''}
        res = self.client.post(TAG_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        