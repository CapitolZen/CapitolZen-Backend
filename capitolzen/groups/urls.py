from django.conf.urls import url, include
from rest_framework import routers
from .endpoints import GroupViewSet

router = routers.SimpleRouter()

router.register(r'groups', GroupViewSet, base_name="organization")

urlpatterns = [
    url(r'^', include(router.urls)),
]
