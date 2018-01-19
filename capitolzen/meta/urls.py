from django.conf.urls import url
from rest_framework_proxy.views import ProxyView

from .views import index

urlpatterns = [
    url(r'^$', index, name="index"),
    url(r'^trivia/(?P<path>.*)$', ProxyView.as_view(), name="proxies"),
]
