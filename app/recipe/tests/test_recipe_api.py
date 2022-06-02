from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

 
RECIPE_URL = reverse('recipe:recipe-list')

def detail_url(recipe_id):
    return reverse('recipe:recipe-detail', args=[recipe_id])

#for sample recipe
def sample_recipe(user, **kwargs):
    defaults = {
        'user': user,
        'title' : 'sample recipe', 
        'time_min': 10,
        'price': 5.00
    }
    defaults.update(kwargs)
    return Recipe.objects.create(**defaults)

def sample_tag(user, name='test tag'):
    return Tag.objects.create(user=user, name=name)

def sample_ingrediant(user, name='test ingrediant'):
    return Ingredient.objects.create(user=user, name=name)


class PublicRecipeApiTest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTest(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email = 'test@gmail.com',
            password = 'test123'
        )
        self.client.force_authenticate(self.user)

    def test_retrive_recipe(self):
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipe = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipe, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_for_limited_user(self):
        user2 = get_user_model().objects.create_user(
            email = 'test1@gmail.com',
            password = 'test123'
        )
        sample_recipe(user=user2)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingrediant.add(sample_ingrediant(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)
        
        serializer = RecipeDetailSerializer(recipe)

    def test_create_recipe_successful(self):
        payload = {
            'title' : 'testtag',
            'time_min': 2,
            'price': 5.00
        }
        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id = res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        tag1 = sample_tag(self.user, name='dessert')
        tag2 = sample_tag(self.user, name='dish')
        payload = {
            'title' : 'avecado',
            'time_min': 2,
            'price': 5.00,
            'tags': [tag1.id, tag2.id]
        }

        res = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id = res.data['id'])
        tag = Tag.objects.all()
        self.assertEqual(tag.count(), 2)
        self.assertIn(tag1, tag)
        self.assertIn(tag2, tag)

    def test_create_recipe_with_ingrediant(self):
        ingrediant1 = sample_ingrediant(self.user, name='dessert')
        ingrediant2 = sample_ingrediant(self.user, name='dish')
        payload = {
            'title' : 'clust',
            'time_min': 20,
            'price': 5.00,
            'ingrediant': [ingrediant1.id, ingrediant2.id]
        }

        res = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id = res.data['id'])
        ingrediant = Ingredient.objects.all()
        self.assertEqual(ingrediant.count(), 2)
        self.assertIn(ingrediant1, ingrediant)
        self.assertIn(ingrediant2, ingrediant)

    def test_partial_update_recipe(self):
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        tag_new = sample_tag(user=self.user, name='dessert')

        payload = {
            'title': 'testrecipe',
            'tags':[tag_new.id],
            'user':self.user
        }
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(tag_new, tags)


    def test_full_update_recipe(self):
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))

        payload = {
            'title': 'testrecipe',
            'time_min': 25,
            'price': 4.99
        }
        url = detail_url(recipe.id)
        self.client.put(url, payload)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(int(recipe.time_min), payload['time_min'])
        self.assertEqual(float(recipe.price), payload['price'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)