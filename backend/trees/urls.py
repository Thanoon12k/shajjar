from django.urls import path

from . import views

app_name = "trees"

urlpatterns = [
    path("my/", views.my_trees, name="my"),
    path("find/", views.lookup, name="lookup"),
    path("<str:code>/", views.detail, name="detail"),
    path("<str:code>/update/", views.add_update, name="update"),
    path("<str:code>/qr.svg", views.qr_svg, name="qr"),
]
