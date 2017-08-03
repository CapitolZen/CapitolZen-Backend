from rest_framework import routers
from .endpoints import BillViewSet, WrapperViewSet, LegislatorViewSet, CommitteeViewSet

router = routers.SimpleRouter()

router.register(r'bills', BillViewSet, base_name="bills")
router.register(r'legislators', LegislatorViewSet, base_name="legislators")
router.register(r'committees', CommitteeViewSet, base_name="committees")
router.register(r'wrappers', WrapperViewSet, base_name="wrappers")

urlpatterns = router.urls
