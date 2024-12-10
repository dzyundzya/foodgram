from django.contrib import admin

from .models import Favorite


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'recipe', 'user'
        )
