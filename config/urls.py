from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^docs/', include('rest_framework_docs.urls')),
    url(r'^health/', include('health_check.urls')),

    url(r'', include('downdraft.meta.urls')),
    url(r'', include('downdraft.organizations.urls')),
    url(r'', include('downdraft.users.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]

handler404 = 'downdraft.meta.views.page_not_found_view'
handler500 = 'downdraft.meta.views.error_view'
handler403 = 'downdraft.meta.views.permission_denied_view'
handler400 = 'downdraft.meta.views.bad_request_view'
