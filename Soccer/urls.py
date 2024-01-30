from django.contrib import admin
from django.urls import path, include
from .schema import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui')
]
