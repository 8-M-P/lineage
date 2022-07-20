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


@login_required
def protected_serve(request, path, document_root=None, show_indexes=False):
    return serve(request, path, document_root, show_indexes)


urlpatterns += [re_path(r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:], protected_serve,
                        {'document_root': settings.MEDIA_ROOT})]
