from rest_framework import routers
from .endpoints import UserViewSet, ActionsViewSet

router = routers.SimpleRouter()
router.register(r'users', UserViewSet, base_name="users")
router.register(r'actions', ActionsViewSet, base_name="actions")
urlpatterns = router.urls
