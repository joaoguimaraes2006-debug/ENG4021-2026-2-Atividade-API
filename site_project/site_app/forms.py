from django import forms

from .models import FilmeSalvo


class FilmeSalvoForm(forms.ModelForm):
    class Meta:
        model = FilmeSalvo
        fields = ["titulo", "diretor", "ano", "nota", "assistido", "poster", "imdb_id"]
        widgets = {
            "titulo": forms.TextInput(attrs={"placeholder": "Ex.: Interestelar"}),
            "diretor": forms.TextInput(attrs={"placeholder": "Ex.: Christopher Nolan"}),
            "ano": forms.NumberInput(attrs={"placeholder": "Ex.: 2014", "min": 1888, "max": 2100}),
            "poster": forms.URLInput(attrs={"placeholder": "https://..."}),
            "imdb_id": forms.TextInput(attrs={"placeholder": "Ex.: tt0816692"}),
        }
