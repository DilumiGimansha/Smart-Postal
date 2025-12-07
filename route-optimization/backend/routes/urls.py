from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MailItemViewSet, RouteViewSet, TrainingLogViewSet

router = DefaultRouter()
router.register(r'mail-items', MailItemViewSet, basename='mail-item')
router.register(r'routes', RouteViewSet, basename='route')
router.register(r'training-logs', TrainingLogViewSet, basename='training-log')

urlpatterns = [
    path('', include(router.urls)),
]