from rest_framework import routers
from .endpoints import UserViewSet, PasswordResetViewSet, FeedViewSet
from django.conf.urls import url

router = routers.SimpleRouter()

router.register(r'users', UserViewSet, base_name="users")
router.register(r'feeds', FeedViewSet, base_name="feeds")

urlpatterns = [
    url(r'password', PasswordResetViewSet.as_view()),
]

urlpatterns += router.urls
