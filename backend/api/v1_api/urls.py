from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .recipes.views import IngredientViewSet, RecipeViewSet
from .tags.views import TagViewSet
from .users.views import DjoserUserViewSet

router = DefaultRouter()

router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'users', DjoserUserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
