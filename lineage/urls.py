from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    path('', include('core.urls'), name='core'),
    path('admin/', admin.site.urls),
]


@login_required
def protected_serve(request, path, document_root=None, show_indexes=False):
    return serve(request, path, document_root, show_indexes)


urlpatterns += [re_path(r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:], protected_serve,
                        {'document_root': settings.MEDIA_ROOT})]
