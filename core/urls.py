from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from django.urls import path, re_path
from django.conf import settings
from django.views.static import serve
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('aile/<str:tag>', home, name='family'),
    path('kisiler/', users, name='users'),
    path('kisiler/<str:tag>', users, name='family_members'),
    path('ailem/', single_user, {'family': True}, name='my_family'),
    path('profilim/', single_user, name='my_profile'),
    path('kisi/<int:pk>', single_user, name='user'),
    path('giris/', login_page, name='login_page'),
    path('cikis/', logout_page, name='logout'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
