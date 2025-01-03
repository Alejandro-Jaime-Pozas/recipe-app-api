"""
URL mappings for the recipe app.
"""
from django.urls import (
    path,
    include,  # to include urls by their specified name
)

from rest_framework.routers import DefaultRouter

from recipe import views

# used to identify this module when using the include, reverse fns elsewhere
app_name = 'recipe'

router = DefaultRouter()  # use to automatically determine url config
router.register('recipes', views.RecipeViewSet)  # this will create auto-generated url endpoints based on the functionality of the view (get, post, put, patch, delete)
router.register('tags', views.TagViewSet)
router.register('ingredients', views.IngredientViewSet)


urlpatterns = [
    path('', include(router.urls)),  # router.urls is where the different auto-generated urls are contained
]
