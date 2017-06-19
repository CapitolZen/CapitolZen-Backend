from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^docs/', include('rest_framework_docs.urls')),
    url(r'^health/', include('health_check.urls')),
    url(r'^api-token-auth/', obtain_jwt_token),
    url(r'^api-token-refresh/', refresh_jwt_token),

    url(r'', include('capitolzen.meta.urls')),
    url(r'', include('capitolzen.organizations.urls')),
    url(r'', include('capitolzen.users.urls')),
    url(r'', include('capitolzen.groups.urls')),
    url(r'', include('capitolzen.proposals.urls'))
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]

handler404 = 'capitolzen.meta.views.page_not_found_view'
handler500 = 'capitolzen.meta.views.error_view'
handler403 = 'capitolzen.meta.views.permission_denied_view'
handler400 = 'capitolzen.meta.views.bad_request_view'
