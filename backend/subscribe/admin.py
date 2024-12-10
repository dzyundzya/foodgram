from django.contrib import admin

from .models import Subscribe


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'user',
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'author', 'user'
        )


