from unittest.mock import Mock, patch

import requests
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import FilmeSalvo


def resposta_falsa(dados):
    resposta = Mock()
    resposta.json.return_value = dados
    resposta.raise_for_status.return_value = None
    return resposta


@override_settings(OMDB_API_KEY="chave-de-teste")
class BuscaFilmesTests(TestCase):
    def test_pagina_inicial_sem_busca(self):
        resposta = self.client.get(reverse("buscar_filmes"))
        self.assertContains(resposta, "Digite o nome de um filme")

    @patch("site_app.views.requests.get")
    def test_busca_com_resultados(self, get):
        get.return_value = resposta_falsa({
            "Response": "True",
            "totalResults": "12",
            "Search": [
                {"Title": "Batman Begins", "Year": "2005", "imdbID": "tt0372784", "Poster": "N/A"},
            ],
        })
        resposta = self.client.get(reverse("buscar_filmes"), {"q": "batman"})
        self.assertContains(resposta, "Batman Begins")
        self.assertContains(resposta, "12 resultados")
        self.assertContains(resposta, "Próxima")
        self.assertEqual(get.call_args.kwargs["params"]["s"], "batman")

    @patch("site_app.views.requests.get")
    def test_busca_sem_resultados(self, get):
        get.return_value = resposta_falsa({"Response": "False", "Error": "Movie not found!"})
        resposta = self.client.get(reverse("buscar_filmes"), {"q": "xyzxyz"})
        self.assertContains(resposta, "Nenhum filme encontrado")

    @patch("site_app.views.requests.get", side_effect=requests.ConnectionError)
    def test_api_fora_do_ar(self, get):
        resposta = self.client.get(reverse("buscar_filmes"), {"q": "batman"})
        self.assertContains(resposta, "Não foi possível falar com a API")

    @patch("site_app.views.requests.get")
    def test_detalhe_do_filme(self, get):
        get.return_value = resposta_falsa({
            "Response": "True", "Title": "Batman Begins", "Year": "2005", "Poster": "N/A",
            "Rated": "PG-13", "Runtime": "140 min", "Genre": "Action", "imdbRating": "8.2",
            "Plot": "Bruce Wayne begins his fight.", "Director": "Christopher Nolan",
            "Actors": "Christian Bale", "Released": "15 Jun 2005", "Language": "English",
        })
        resposta = self.client.get(reverse("detalhe_filme", args=["tt0372784"]))
        self.assertContains(resposta, "Christopher Nolan")
        self.assertContains(resposta, "8.2/10")

    @patch("site_app.views.requests.get")
    def test_detalhe_inexistente_da_404(self, get):
        get.return_value = resposta_falsa({"Response": "False", "Error": "Incorrect IMDb ID."})
        resposta = self.client.get(reverse("detalhe_filme", args=["tt0000000"]))
        self.assertEqual(resposta.status_code, 404)


@override_settings(OMDB_API_KEY="")
class SemChaveTests(TestCase):
    def test_avisa_que_falta_a_chave(self):
        resposta = self.client.get(reverse("buscar_filmes"), {"q": "batman"})
        self.assertContains(resposta, "Configure a chave da API")


class MinhaListaCrudTests(TestCase):
    def setUp(self):
        self.filme = FilmeSalvo.objects.create(titulo="Interestelar", diretor="Christopher Nolan", ano=2014)

    def test_read_lista_os_filmes(self):
        resposta = self.client.get(reverse("minha_lista"))
        self.assertContains(resposta, "Interestelar")
        self.assertContains(resposta, reverse("editar_filme", args=[self.filme.id]))
        self.assertContains(resposta, reverse("remover_filme", args=[self.filme.id]))

    def test_create_pelo_formulario(self):
        resposta = self.client.post(reverse("minha_lista"), {"titulo": "Duna", "ano": "2021", "nota": "9"})
        self.assertRedirects(resposta, reverse("minha_lista"))
        self.assertTrue(FilmeSalvo.objects.filter(titulo="Duna", nota=9).exists())

    def test_create_sem_titulo_mostra_erro(self):
        self.client.post(reverse("minha_lista"), {"titulo": ""})
        self.assertEqual(FilmeSalvo.objects.count(), 1)

    def test_filtro_assistidos(self):
        FilmeSalvo.objects.create(titulo="Matrix", assistido=True)
        resposta = self.client.get(reverse("minha_lista"), {"filtro": "assistidos"})
        self.assertContains(resposta, "Matrix")
        self.assertNotContains(resposta, "<h2>Interestelar")

    def test_update_mostra_formulario_preenchido(self):
        resposta = self.client.get(reverse("editar_filme", args=[self.filme.id]))
        self.assertContains(resposta, 'value="Interestelar"')

    def test_update_salva(self):
        self.client.post(reverse("editar_filme", args=[self.filme.id]), {
            "titulo": "Interestelar", "diretor": "Christopher Nolan", "ano": "2014",
            "nota": "10", "assistido": "on",
        })
        self.filme.refresh_from_db()
        self.assertEqual(self.filme.nota, 10)
        self.assertTrue(self.filme.assistido)

    def test_delete_pede_confirmacao(self):
        resposta = self.client.get(reverse("remover_filme", args=[self.filme.id]))
        self.assertContains(resposta, "Remover “Interestelar” da sua lista?")
        self.assertTrue(FilmeSalvo.objects.filter(id=self.filme.id).exists())

    def test_delete_remove(self):
        resposta = self.client.post(reverse("remover_filme", args=[self.filme.id]))
        self.assertRedirects(resposta, reverse("minha_lista"))
        self.assertFalse(FilmeSalvo.objects.filter(id=self.filme.id).exists())

    def test_id_inexistente_da_404(self):
        self.assertEqual(self.client.get(reverse("editar_filme", args=[999])).status_code, 404)


@override_settings(OMDB_API_KEY="chave-de-teste")
class SalvarDaApiTests(TestCase):
    @patch("site_app.views.requests.get")
    def test_salva_filme_da_api(self, get):
        get.return_value = resposta_falsa({
            "Response": "True", "Title": "Batman Begins", "Year": "2005",
            "Director": "Christopher Nolan", "Poster": "N/A",
        })
        resposta = self.client.post(reverse("salvar_da_api", args=["tt0372784"]))
        self.assertRedirects(resposta, reverse("minha_lista"))
        filme = FilmeSalvo.objects.get(imdb_id="tt0372784")
        self.assertEqual(filme.titulo, "Batman Begins")
        self.assertEqual(filme.ano, 2005)
        self.assertEqual(filme.poster, "")

    @patch("site_app.views.requests.get")
    def test_nao_duplica(self, get):
        existente = FilmeSalvo.objects.create(titulo="Batman Begins", imdb_id="tt0372784")
        resposta = self.client.post(reverse("salvar_da_api", args=["tt0372784"]))
        self.assertRedirects(resposta, reverse("editar_filme", args=[existente.id]))
        self.assertEqual(FilmeSalvo.objects.count(), 1)
        get.assert_not_called()
