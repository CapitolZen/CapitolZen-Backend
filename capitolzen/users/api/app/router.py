from rest_framework import routers
from .endpoints import UserViewSet

router = routers.SimpleRouter()
router.register(r'users', UserViewSet, base_name="users")
urlpatterns = router.urls
