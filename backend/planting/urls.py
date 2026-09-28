from django.urls import path

from . import views

app_name = "planting"

urlpatterns = [
    path("", views.map_view, name="map"),
    path("data.json", views.map_data, name="data"),
    path("site/<int:pk>/", views.site_detail, name="site"),
]
