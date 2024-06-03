from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('sns.urls')),
    # path('api-auth/', include('rest_framework.urls')),  # For browsable API login/logout
    # path('api-token-auth/', obtain_auth_token),
]
