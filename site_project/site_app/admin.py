from django.contrib import admin

from .models import FilmeSalvo


@admin.register(FilmeSalvo)
class FilmeSalvoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "ano", "nota", "assistido")
    list_filter = ("assistido",)
    search_fields = ("titulo", "diretor")
