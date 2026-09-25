from django.urls import path

from . import views

app_name = "tree_requests"

urlpatterns = [
    path("new/", views.new_request, name="new"),
    path("my/", views.my_requests, name="my"),
    path("<str:code>/", views.detail, name="detail"),
]
