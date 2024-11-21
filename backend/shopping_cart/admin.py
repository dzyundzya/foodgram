from django.contrib import admin

from .models import ShoppingCart


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )


admin.site.register(ShoppingCart, ShoppingCartAdmin)
