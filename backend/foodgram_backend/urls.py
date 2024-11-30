from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from api.v1_api.recipes.views import short_url


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('s/<int:pk>', short_url, name='short_url')
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)
