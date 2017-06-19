from django.conf.urls import url, include
from rest_framework import routers
from .endpoints import UserViewSet

router = routers.SimpleRouter()

router.register(r'users', UserViewSet, base_name="users")

urlpatterns = [
    url(r'^', include(router.urls))
]
