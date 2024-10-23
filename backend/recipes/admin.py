from django.contrib import admin

from .models import (
    Favorite, Ingredient, IngredientInRecipe, Recipe, ShoppingCart, Tag
)


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    list_filter = (
        'name',
    )


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
    )
    list_filter = (
        'name',
        'author',
        'tags',
    )
    filter_horizontal = (
        'ingredients',
        'tags',
    )


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )


class IngredientInRecipeAdmin(admin.ModelAdmin):
    list_display = (
        'recipe',
        'ingredient',
        'amount',
    )


class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(IngredientInRecipe, IngredientInRecipeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
