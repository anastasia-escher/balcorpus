# urls.py

from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
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

if settings.DEBUG:
    schema_view = get_schema_view(
        openapi.Info(
            title="NEXUS Full Stack API",
            default_version="v1",
            description=(
                "This is the NEXUS full stack example API overview. You "
                "should be able to see all the endpoints available in the API."
            ),
        ),
        url="http://localhost:8077/api/v1/",
        public=True,
    )

    urlpatterns += [
        path(
            "api/v1/swagger<format>/",
            schema_view.without_ui(cache_timeout=0),
            name="schema-json",
        ),
        path(
            "api/v1/swagger/",
            schema_view.with_ui("swagger", cache_timeout=0),
            name="schema-swagger-ui",
        ),
    ]