from django.conf.urls import url, include
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns

from capitolzen.proposals.api.app.endpoints import (
    BillViewSet, WrapperViewSet, LegislatorViewSet, CommitteeViewSet,
    BillSearchView
)

router = routers.SimpleRouter()

router.register(r'bills', BillViewSet, base_name="bills")
router.register(r'legislators', LegislatorViewSet, base_name="legislators")
router.register(r'committees', CommitteeViewSet, base_name="committees")
router.register(r'wrappers', WrapperViewSet, base_name="wrappers")

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^search/$', BillSearchView.as_view(), name='bill_search')
]

urlpatterns = format_suffix_patterns(urlpatterns)
