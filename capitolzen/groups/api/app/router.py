from django.conf.urls import url, include
from rest_framework import routers
from .endpoints import GroupViewSet, ReportViewSet, FileViewSet

router = routers.SimpleRouter()

router.register(r'groups', GroupViewSet, base_name="groups")
router.register(r'reports', ReportViewSet, base_name="report")
router.register(r'files', FileViewSet, base_name="files")

urlpatterns = [
    url(r'^', include(router.urls)),
]
