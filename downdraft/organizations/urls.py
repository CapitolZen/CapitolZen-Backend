from django.conf.urls import url, include
from rest_framework import routers
from .endpoints import (OrganizationViewSet, OrganizationInviteViewSet)

router = routers.SimpleRouter()

router.register(r'organizations', OrganizationViewSet, base_name="organization")
router.register(r'invites', OrganizationInviteViewSet, base_name="invite")

urlpatterns = [
    url(r'^', include(router.urls)),
]
