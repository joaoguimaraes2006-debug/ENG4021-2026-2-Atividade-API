# ENG4021 - Atividade API (filmes)

Site em Django que consome a API do [OMDb](https://www.omdbapi.com/) para buscar filmes e mostrar os detalhes de cada um.

## Funcionalidades

- Busca de filmes pelo nome, com paginação
- Lista com pôster, título e ano
- Tela de detalhes (sinopse, nota no IMDb, direção, elenco, gênero e duração)
- Mensagens de erro quando não há resultados ou a API não responde

## Como rodar

```bash
pip install -r requirements.txt
cd site_project
export OMDB_API_KEY="sua_chave"   # no Windows: set OMDB_API_KEY=sua_chave
python manage.py runserver
```

A chave do OMDb é gratuita e pode ser pedida em https://www.omdbapi.com/apikey.aspx.

## Estrutura

- `site_project/` - projeto Django (`settings.py`, `urls.py`)
- `site_project/site_app/` - app com as views e os testes
- `template/` - páginas HTML (`index.html` e `detalhe.html`)
- `static/` - CSS (`style.css`)
