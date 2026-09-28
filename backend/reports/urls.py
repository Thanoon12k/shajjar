from django.urls import path

from . import views

app_name = "reports"

urlpatterns = [
    path("new/", views.new_report, name="new"),
    path("my/", views.my_reports, name="my"),
    path("<str:code>/", views.detail, name="detail"),
]
