import requests
from django.conf import settings
from django.http import Http404
from django.shortcuts import render


def consultar_omdb(parametros):
    """Faz uma requisição à API do OMDb e devolve (dados, erro)."""
    if not settings.OMDB_API_KEY:
        return None, "Configure a chave da API (OMDB_API_KEY) no settings.py para buscar filmes."

    parametros = {**parametros, "apikey": settings.OMDB_API_KEY}

    try:
        resposta = requests.get(settings.OMDB_URL, params=parametros, timeout=10)
        resposta.raise_for_status()
        return resposta.json(), None
    except requests.RequestException:
        return None, "Não foi possível falar com a API do OMDb agora. Tente de novo em instantes."


def buscar_filmes(request):
    """Tela inicial: campo de busca e lista de filmes encontrados."""
    termo = request.GET.get("q", "").strip()
    pagina = request.GET.get("page", "1")
    if not pagina.isdigit() or int(pagina) < 1:
        pagina = "1"
    pagina = int(pagina)

    filmes = []
    total = 0
    erro = None

    if termo:
        dados, erro = consultar_omdb({"s": termo, "type": "movie", "page": pagina})
        if dados:
            if dados.get("Response") == "True":
                filmes = dados.get("Search", [])
                total = int(dados.get("totalResults", 0))
            else:
                erro = f"Nenhum filme encontrado para “{termo}”."

    total_paginas = (total + 9) // 10  # o OMDb devolve 10 filmes por página

    contexto = {
        "termo": termo,
        "filmes": filmes,
        "total": total,
        "erro": erro,
        "pagina": pagina,
        "pagina_anterior": pagina - 1 if pagina > 1 else None,
        "proxima_pagina": pagina + 1 if pagina < total_paginas else None,
    }
    return render(request, "index.html", contexto)


def detalhe_filme(request, imdb_id):
    """Tela de detalhes de um filme, buscado pelo código do IMDb."""
    dados, erro = consultar_omdb({"i": imdb_id, "plot": "full"})

    if dados and dados.get("Response") != "True":
        raise Http404("Filme não encontrado")

    contexto = {
        "filme": dados,
        "erro": erro,
        "voltar": request.GET.get("q", ""),
    }
    return render(request, "detalhe.html", contexto)
