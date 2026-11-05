import requests
from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from .forms import FilmeSalvoForm
from .models import FilmeSalvo


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
        "imdb_id": imdb_id,
        "salvo": FilmeSalvo.objects.filter(imdb_id=imdb_id).first(),
    }
    return render(request, "detalhe.html", contexto)


# ---------------------------------------------------------------------------
# CRUD da "Minha lista" (Create, Read, Update e Delete de FilmeSalvo)
# ---------------------------------------------------------------------------

def minha_lista(request):
    """Read + Create: mostra os filmes salvos e o formulário para adicionar um novo."""
    if request.method == "POST":
        form = FilmeSalvoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("minha_lista")
    else:
        form = FilmeSalvoForm()

    filtro = request.GET.get("filtro", "")
    filmes = FilmeSalvo.objects.all()
    if filtro == "assistidos":
        filmes = filmes.filter(assistido=True)
    elif filtro == "quero-ver":
        filmes = filmes.filter(assistido=False)

    contexto = {
        "filmes": filmes,
        "form": form,
        "filtro": filtro,
        "total": FilmeSalvo.objects.count(),
    }
    return render(request, "minha_lista.html", contexto)


def salvar_da_api(request, imdb_id):
    """Create a partir da API: salva na lista o filme aberto na tela de detalhes."""
    if request.method != "POST":
        return redirect("detalhe_filme", imdb_id=imdb_id)

    existente = FilmeSalvo.objects.filter(imdb_id=imdb_id).first()
    if existente:
        return redirect("editar_filme", filme_id=existente.id)

    dados, erro = consultar_omdb({"i": imdb_id})
    if erro or not dados or dados.get("Response") != "True":
        raise Http404("Filme não encontrado")

    ano = dados.get("Year", "")[:4]
    FilmeSalvo.objects.create(
        titulo=dados.get("Title", ""),
        diretor="" if dados.get("Director") == "N/A" else dados.get("Director", ""),
        ano=int(ano) if ano.isdigit() else None,
        imdb_id=imdb_id,
        poster="" if dados.get("Poster") == "N/A" else dados.get("Poster", ""),
    )
    return redirect("minha_lista")


def editar_filme(request, filme_id):
    """Update: abre o formulário já preenchido e salva as alterações."""
    filme = get_object_or_404(FilmeSalvo, id=filme_id)

    if request.method == "POST":
        form = FilmeSalvoForm(request.POST, instance=filme)
        if form.is_valid():
            form.save()
            return redirect("minha_lista")
    else:
        form = FilmeSalvoForm(instance=filme)

    return render(request, "editar_filme.html", {"form": form, "filme": filme})


def remover_filme(request, filme_id):
    """Delete: pede confirmação (GET) e só apaga quando a pessoa confirma (POST)."""
    filme = get_object_or_404(FilmeSalvo, id=filme_id)

    if request.method == "POST":
        filme.delete()
        return redirect("minha_lista")

    return render(request, "remover_filme.html", {"filme": filme})
