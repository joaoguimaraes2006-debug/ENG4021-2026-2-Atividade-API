from django.contrib import admin
from django.urls import path

from site_app import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.buscar_filmes, name="buscar_filmes"),
    path("filme/<str:imdb_id>/", views.detalhe_filme, name="detalhe_filme"),
    path("filme/<str:imdb_id>/salvar/", views.salvar_da_api, name="salvar_da_api"),
    path("minha-lista/", views.minha_lista, name="minha_lista"),
    path("minha-lista/<int:filme_id>/editar/", views.editar_filme, name="editar_filme"),
    path("minha-lista/<int:filme_id>/remover/", views.remover_filme, name="remover_filme"),
]
