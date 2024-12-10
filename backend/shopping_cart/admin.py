from django.contrib import admin

from .models import ShoppingCart


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'recipe', 'user'
        )
