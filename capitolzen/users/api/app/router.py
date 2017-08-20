from rest_framework import routers
from .endpoints import UserViewSet, PasswordResetViewSet, ActivityViewSet
from django.conf.urls import url

router = routers.SimpleRouter()

router.register(r'users', UserViewSet, base_name="users")
router.register(r'activities', ActivityViewSet, base_name="activities")

urlpatterns = [
    url(r'password', PasswordResetViewSet.as_view()),
]

urlpatterns += router.urls
