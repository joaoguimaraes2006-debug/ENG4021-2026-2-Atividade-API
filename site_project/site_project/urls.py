from django.contrib import admin
from django.urls import path

from site_app import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.buscar_filmes, name="buscar_filmes"),
    path("filme/<str:imdb_id>/", views.detalhe_filme, name="detalhe_filme"),
]
