from django.conf.urls import url, include
from rest_framework import routers
from .endpoints import GroupViewSet, ReportViewSet, FileViewSet, UpdateViewSet, PageViewSet, LinkViewSet

router = routers.SimpleRouter()

router.register(r'groups', GroupViewSet, base_name="groups")
router.register(r'reports', ReportViewSet, base_name="report")
router.register(r'files', FileViewSet, base_name="files")
router.register(r'updates', UpdateViewSet, base_name="updates")
router.register(r'pages', PageViewSet, base_name="pages")
router.register(r'links', LinkViewSet, base_name="links")

urlpatterns = [
    url(r'^', include(router.urls)),
]
