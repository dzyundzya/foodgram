from typing import Any
from djaa_list_filter.admin import AjaxAutocompleteListFilterModelAdmin
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest


from .models import Ingredient, IngredientInRecipe, Recipe


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = (
        'name',
    )


@admin.register(Recipe)
class RecipeAdmin(AjaxAutocompleteListFilterModelAdmin):
    list_display = (
        'name',
        'author',
    )
    autocomplete_list_filter = (
        'author',
        'tags',
    )
    search_fields = (
        'name',
    )
    filter_horizontal = (
        'ingredients',
        'tags',
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'author'
        ).prefetch_related(
            'tags', 'ingredients'
        )


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    list_display = (
        'recipe',
        'ingredient',
        'amount',
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'recipe', 'ingredient'
        )
