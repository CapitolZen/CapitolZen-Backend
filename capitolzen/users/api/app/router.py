from rest_framework import routers
from .endpoints import UserViewSet, PasswordResetViewSet
from django.conf.urls import url

router = routers.SimpleRouter()

router.register(r'users', UserViewSet, base_name="users")

urlpatterns = [
    url(r'password', PasswordResetViewSet.as_view()),
]

urlpatterns += router.urls
