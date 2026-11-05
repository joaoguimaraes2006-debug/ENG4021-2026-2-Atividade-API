from django.db import models


class FilmeSalvo(models.Model):
    """Filme que o usuário guardou na sua lista (pode vir da API ou ser cadastrado à mão)."""

    titulo = models.CharField("Título", max_length=150)
    diretor = models.CharField("Direção", max_length=150, blank=True)
    ano = models.PositiveIntegerField("Ano", null=True, blank=True)
    imdb_id = models.CharField("Código IMDb", max_length=20, blank=True)
    poster = models.URLField("Pôster (link)", max_length=500, blank=True)
    nota = models.PositiveSmallIntegerField(
        "Minha nota (0 a 10)", null=True, blank=True,
        choices=[(None, "Sem nota")] + [(n, str(n)) for n in range(11)],
    )
    assistido = models.BooleanField("Já assisti", default=False)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "filme salvo"
        verbose_name_plural = "filmes salvos"

    def __str__(self):
        return self.titulo
