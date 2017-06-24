from django.conf.urls import url, include
from rest_framework import routers
from .endpoints import AlertsViewSet

router = routers.SimpleRouter()

router.register(r'alerts', AlertsViewSet, base_name="alerts")

urlpatterns = [
    url(r'^', include(router.urls))
]
