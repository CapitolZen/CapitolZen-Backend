from django.conf.urls import url, include
from rest_framework import routers
from .endpoints import BillViewSet

router = routers.SimpleRouter()

router.register(r'bills', ProposalViewSet, base_name="bills")

urlpatterns = [
    url(r'^', include(router.urls)),
]
