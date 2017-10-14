from django.conf.urls import url, include
from rest_framework import routers

from .endpoints import ActivityViewSet, FileManagerView

router = routers.SimpleRouter()

router.register(r'activities', ActivityViewSet, base_name="activities")

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^files/$', FileManagerView.as_view(), name="action-list"),
]
