from rest_framework import routers
from .endpoints import UserViewSet, NotificationViewSet, PasswordResetViewSet
from django.conf.urls import url

router = routers.SimpleRouter()

router.register(r'users', UserViewSet, base_name="users")
router.register(r'notifications', NotificationViewSet, base_name="notification")
urlpatterns = [
    url(r'password', PasswordResetViewSet.as_view())
]

urlpatterns += router.urls
