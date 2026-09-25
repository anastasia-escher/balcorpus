from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from core.views import (
    TextViewSet,
    SpeakerViewSet,
    SentenceViewSet,
    TokenViewSet,
)


router = DefaultRouter()
router.register(r"texts", TextViewSet, basename="text")
router.register(r"speakers", SpeakerViewSet, basename="speaker")
router.register(r"sentences", SentenceViewSet, basename="sentence")
router.register(r"tokens", TokenViewSet, basename="token")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(router.urls)),
]
