from rest_framework import routers
from .endpoints import UserViewSet, AlertsViewSet

router = routers.SimpleRouter()

router.register(r'users', UserViewSet, base_name="users")
router.register(r'alerts', AlertsViewSet, base_name="alerts")

urlpatterns = router.urls
