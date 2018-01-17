from django.conf.urls import url

from .views import index, TriviaProxyView

urlpatterns = [
    url(r'^$', index, name="index"),
    url(r'^trivia/(?P<path>.*)$', TriviaProxyView.as_view(), name="proxies"),
]
