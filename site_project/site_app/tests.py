from unittest.mock import Mock, patch

import requests
from django.test import TestCase, override_settings
from django.urls import reverse


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
