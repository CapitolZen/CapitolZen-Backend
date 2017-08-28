from rest_framework import routers
from .endpoints import ActivityViewSet

router = routers.SimpleRouter()

router.register(r'activities', ActivityViewSet, base_name="activities")

urlpatterns = router.urls
