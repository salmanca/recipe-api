from django.urls import path, include
from rest_framework.routers import DefaultRouter
from recipe.views import RecipeViewSet
from recipe import views    

router = DefaultRouter()
router.register('tags', views.TagViewSet)
router.register('ingredient', views.IngredientViewSet)
router.register('recipe',RecipeViewSet)
router.register('recipe-detail',RecipeViewSet)

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls)),
]

