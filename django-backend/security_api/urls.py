from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'tools', views.SecurityToolViewSet)
router.register(r'vulnerabilities', views.VulnerabilityViewSet)
router.register(r'alerts', views.SecurityAlertViewSet)
router.register(r'scans', views.ScanResultViewSet)
router.register(r'hosts', views.NetworkHostViewSet)
router.register(r'metrics', views.SecurityMetricViewSet)
router.register(r'dashboard', views.DashboardViewSet, basename='dashboard')
router.register(r'scan-schedules', views.ScanScheduleViewSet, basename='scan-schedule')
urlpatterns = [
    path('', include(router.urls)),
]
