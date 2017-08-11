from rest_framework import routers
from .endpoints import UserViewSet, AlertsViewSet, PasswordResetViewSet
from django.conf.urls import url

router = routers.SimpleRouter()

router.register(r'users', UserViewSet, base_name="users")
router.register(r'alerts', AlertsViewSet, base_name="alerts")
urlpatterns = [
    url(r'password', PasswordResetViewSet.as_view())
]

urlpatterns += router.urls
