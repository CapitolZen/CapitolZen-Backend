from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token
from rest_framework.documentation import include_docs_urls

app_api_urls = [
    url(r'', include('capitolzen.organizations.api.app.router')),
    url(r'', include('capitolzen.users.api.app.router')),
    url(r'', include('capitolzen.groups.api.app.router')),
    url(r'', include('capitolzen.proposals.api.app.router')),
    url(r'', include('capitolzen.meta.api.app.router')),
]

urlpatterns = [
    url(r'', include('capitolzen.meta.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^docs/', include_docs_urls(title='API', patterns=app_api_urls)),
    url(r'^health/', include('health_check.urls')),

    url(r'^auth/', include('rest_auth.urls')),
    url(r'^api-token-auth/', obtain_jwt_token),
    url(r'^api-token-refresh/', refresh_jwt_token),
]

urlpatterns += app_api_urls

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]

handler404 = 'capitolzen.meta.views.page_not_found_view'
handler500 = 'capitolzen.meta.views.error_view'
handler403 = 'capitolzen.meta.views.permission_denied_view'
handler400 = 'capitolzen.meta.views.bad_request_view'
