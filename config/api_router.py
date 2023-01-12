from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from django_storage_test.users.api.views import UserViewSet
from django_storage_test.videos.api.views import VideoViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register("videos", VideoViewSet)

app_name = "api"
urlpatterns = router.urls
