from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from apps.camerastream.api import (
    CameraViewSet,
    DashboardSummaryView,
    EntryCarLogViewSet,
    EntryPersonLogViewSet,
)
from apps.data.api import CarViewSet, PersonViewSet
from .views import *

api_router = DefaultRouter()
api_router.register('cameras', CameraViewSet, basename='camera')
api_router.register('persons', PersonViewSet, basename='person')
api_router.register('cars', CarViewSet, basename='car')
api_router.register('logs/persons', EntryPersonLogViewSet, basename='person-log')
api_router.register('logs/cars', EntryCarLogViewSet, basename='car-log')

urlpatterns = [
    path('', home, name='home'),
    path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    path('secret/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('database/', include('apps.data.urls')),
    path('dashboard/', include('apps.camerastream.urls')),

    # REST API consumed by the dashboard and by external clients
    path('api/', include(api_router.urls)),
    path('api/summary/', DashboardSummaryView.as_view(), name='api-summary'),
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token-obtain'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='api-docs',
    ),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()