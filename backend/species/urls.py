from django.urls import path

from . import views

app_name = "species"

urlpatterns = [
    path("", views.encyclopedia, name="list"),
    path("<int:pk>/", views.detail, name="detail"),
]
