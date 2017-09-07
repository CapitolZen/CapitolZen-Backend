from django.conf.urls import url, include
from rest_framework import routers
from .endpoints import GroupViewSet, ReportViewSet

router = routers.SimpleRouter()

router.register(r'groups', GroupViewSet, base_name="groups")
router.register(r'reports', ReportViewSet, base_name="report")

urlpatterns = [
    url(r'^', include(router.urls)),
]
