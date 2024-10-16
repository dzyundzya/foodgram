from django.urls import include, path


urlpatterns = [
    path('', include('api.v1_api.urls')),
]
