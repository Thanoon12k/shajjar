from django.urls import path

from . import views

app_name = "campaigns"

urlpatterns = [
    path("", views.campaign_list, name="list"),
    path("<int:pk>/", views.detail, name="detail"),
    path("<int:pk>/join/", views.join, name="join"),
    path("<int:pk>/leave/", views.leave, name="leave"),
]
