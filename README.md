# ENG4021 - Atividade API (filmes)

Site em Django que consome a API do [OMDb](https://www.omdbapi.com/) para buscar filmes e mostrar os detalhes de cada um, com uma "Minha lista" de filmes salvos no banco (CRUD).

## Funcionalidades

- Busca de filmes pelo nome, com paginação
- Lista com pôster, título e ano
- Tela de detalhes (sinopse, nota no IMDb, direção, elenco, gênero e duração)
- Mensagens de erro quando não há resultados ou a API não responde
- **Minha lista (CRUD)** com o model `FilmeSalvo`:
  - **Create**: botão "Salvar na minha lista" na tela de detalhes (puxa os dados da API) ou formulário para cadastrar à mão
  - **Read**: página `/minha-lista/` com todos os filmes salvos e filtro Todos / Quero ver / Assistidos
  - **Update**: tela de edição (nota de 0 a 10, "já assisti", ano, direção...)
  - **Delete**: tela de confirmação antes de remover

## Como rodar

```bash
pip install -r requirements.txt
cd site_project
export OMDB_API_KEY="sua_chave"   # no Windows: set OMDB_API_KEY=sua_chave
python manage.py migrate
python manage.py runserver
```

A chave do OMDb é gratuita e pode ser pedida em https://www.omdbapi.com/apikey.aspx.

## Estrutura

- `site_project/` - projeto Django (`settings.py`, `urls.py`)
- `site_project/site_app/` - app com o model, o formulário, as views e os testes
- `template/` - páginas HTML (`index.html`, `detalhe.html`, `minha_lista.html`, `editar_filme.html` e `remover_filme.html`)
- `static/` - CSS (`style.css`)
