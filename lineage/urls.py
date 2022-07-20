from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('core.urls'), name='core'),
    path('admin/', admin.site.urls),
]
