from django.conf.urls import url, include
from rest_framework import routers
from .endpoints import BillViewSet, WrapperViewSet

router = routers.SimpleRouter()

router.register(r'bills', BillViewSet, base_name="bills")
router.register(r'wrappers', WrapperViewSet, base_name="wrappers")

urlpatterns = [
    url(r'^', include(router.urls)),
]
