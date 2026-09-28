from django.urls import path

from . import views

app_name = "content"

urlpatterns = [
    path("", views.article_list, name="list"),
    path("law/", views.law, name="law"),
    path("contribute/", views.contribute, name="contribute"),
    path("<str:slug>/", views.article, name="article"),
]
