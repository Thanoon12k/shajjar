from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("impact/", views.impact, name="impact"),
    path("about/", views.about, name="about"),
    path("me/", views.activity, name="activity"),
    path("notifications/", views.notifications, name="notifications"),
    path("notifications/<int:pk>/read/", views.notification_read, name="notification_read"),
    path("notifications/read-all/", views.notifications_read_all, name="notifications_read_all"),
    path("dashboard/", views.dashboard, name="dashboard"),
]
