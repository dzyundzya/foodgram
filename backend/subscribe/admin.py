from django.contrib import admin

from .models import Subscribe


class SubscribeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'author',
        'user',
    )


admin.site.register(Subscribe, SubscribeAdmin)
