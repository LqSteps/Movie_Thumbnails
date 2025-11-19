# Movie_Thumbnails

Serviço Python automatizado para extração de URLs de pôsteres e banners de filmes/séries em múltiplas resoluções e idiomas via TMDB API, **excluindo imagens sem texto**.

## Visão Geral

O Movie_Thumbnails lê títulos de filmes/séries de uma planilha Google Sheets, busca cada item no TMDB e extrai **todas as imagens COM idioma** (pôsteres e backdrops), filtrando programaticamente imagens internacionais sem texto (`iso_639_1 = null`). Gera URLs para múltiplas resoluções otimizadas para uso responsivo em web.

## Fonte de Dados

### Planilha Google Sheets

**URL da Planilha**: [https://docs.google.com/spreadsheets/d/1Mj8CovNSu03bpWnIGp_JntDUhxw5KjLRhbfqr8VfsHk/export?format=csv&gid=0](https://docs.google.com/spreadsheets/d/1Mj8CovNSu03bpWnIGp_JntDUhxw5KjLRhbfqr8VfsHk/export?format=csv&gid=0)

**Formato Suportado**: 

- Coluna única com títulos de filmes/séries
- Formatos aceitos:
  - `Nome do Filme (2024)`
  - `Nome do Filme - 2024`
  - `Nome do Filme` (sem ano)

## Funcionalidades Principais

### Filtro Inteligente de Imagens

**DIFERENCIAL**: O sistema busca **TODAS as imagens** via API do TMDB (sem filtro de idioma) e então **filtra programaticamente** apenas as imagens que possuem `iso_639_1` (código de idioma) definido.

```python
# Filtro aplicado no código (linha ~145):
posters = [p for p in all_posters if p.get("iso_639_1") is not None]
backdrops = [b for b in all_backdrops if b.get("iso_639_1") is not None]
```

**Resultado**: Remove imagens internacionais sem texto, mantendo apenas versões localizadas.

**Exemplo de remoção**:
```
🌐 Buscando todas as imagens...
   Total retornado pela API: 18 posters + 14 backdrops
🗑️  Removido: 3 posters + 2 backdrops sem texto (null)
   Final processado: 15 posters + 12 backdrops
```

### Resoluções Disponíveis

#### Pôsteres (Posters)

| Device | Largura | Tamanho TMDB | Peso Aprox. | Uso Recomendado |
|--------|---------|--------------|-------------|-----------------|
| Mobile | 342px | `w342` | ~50-80KB | Smartphones, thumbnails |
| Tablet | 500px | `w500` | ~100-150KB | Tablets, lista desktop |
| Desktop | 780px | `w780` | ~180-250KB | HD, página de detalhes |
| TV | Original | `original` | ~400KB-2MB | 4K, impressão, zoom |

**Definido no código**:
```python
POSTER_SIZES = {
    "mobile": "w342",
    "tablet": "w500",
    "desktop": "w780",
    "tv": "original"
}
```

#### Banners (Backdrops)

| Device | Largura | Tamanho TMDB | Peso Aprox. | Uso Recomendado |
|--------|---------|--------------|-------------|-----------------|
| Mobile | 300px | `w300` | ~30-50KB | Smartphones portrait |
| Tablet | 780px | `w780` | ~120-180KB | Mobile landscape, tablet |
| Desktop | 1280px | `w1280` | ~200-350KB | Desktop HD, hero sections |
| TV | Original | `original` | ~500KB-3MB | 4K, fullscreen, wallpapers |

**Definido no código**:
```python
BACKDROP_SIZES = {
    "mobile": "w300",
    "tablet": "w780",
    "desktop": "w1280",
    "tv": "original"
}
```

### URLs Geradas

Para cada imagem, o sistema gera 4 URLs completas prontas para uso:

```
https://image.tmdb.org/t/p/{size}{file_path}
```

**Exemplo real de poster do The Matrix**:
```
https://image.tmdb.org/t/p/w342/qJ2tW6WMUDux911r6m7haRef0WH.jpg    (342px - mobile)
https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg    (500px - tablet)
https://image.tmdb.org/t/p/w780/qJ2tW6WMUDux911r6m7haRef0WH.jpg    (780px - desktop)
https://image.tmdb.org/t/p/original/qJ2tW6WMUDux911r6m7haRef0WH.jpg (original - 4K)
```

## Estrutura do Projeto

```
Movie_Thumbnails/
├── venv/                              # Ambiente virtual (já configurado)
├── main.py                            # Script principal (~400 linhas)
├── Images/                            # Diretório de saída
│   ├── The Matrix (1999)/
│   │   └── images.json                # Imagens específicas do filme
│   ├── Inception (2010)/
│   │   └── images.json
│   ├── [SERIE] Breaking Bad (2008)/
│   │   └── images.json
│   ├── [SERIE] Game of Thrones (2011)/
│   │   └── images.json
│   └── all_content.json               # JSON consolidado de TUDO
└── movie-thumbnails.service           # Arquivo systemd
```

## Formato dos Arquivos de Saída

### 1. `{nome_filme}/images.json` (Individual)

Arquivo JSON completo com todas as imagens de um único filme/série.

**Exemplo completo - The Matrix (1999)/images.json**:

```json
{
  "id": 603,
  "type": "movie",
  "title": "The Matrix",
  "original_title": "The Matrix",
  "release_date": "1999-03-30",
  "overview": "Thomas A. Anderson é um jovem programador...",
  "year_from_sheet": "1999",
  "posters": [
    {
      "file_path": "/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
      "language": "en",
      "vote_average": 5.384,
      "width": 2000,
      "height": 3000,
      "urls": {
        "mobile": "https://image.tmdb.org/t/p/w342/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
        "tablet": "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
        "desktop": "https://image.tmdb.org/t/p/w780/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
        "tv": "https://image.tmdb.org/t/p/original/qJ2tW6WMUDux911r6m7haRef0WH.jpg"
      }
    },
    {
      "file_path": "/dXNAPwY7VrqMAo51EKhhCJfaGb5.jpg",
      "language": "pt",
      "vote_average": 5.252,
      "width": 1382,
      "height": 2048,
      "urls": {
        "mobile": "https://image.tmdb.org/t/p/w342/dXNAPwY7VrqMAo51EKhhCJfaGb5.jpg",
        "tablet": "https://image.tmdb.org/t/p/w500/dXNAPwY7VrqMAo51EKhhCJfaGb5.jpg",
        "desktop": "https://image.tmdb.org/t/p/w780/dXNAPwY7VrqMAo51EKhhCJfaGb5.jpg",
        "tv": "https://image.tmdb.org/t/p/original/dXNAPwY7VrqMAo51EKhhCJfaGb5.jpg"
      }
    },
    {
      "file_path": "/aOIuZAjPaRIE74ryCFFn0zNfqFF.jpg",
      "language": "es",
      "vote_average": 5.18,
      "width": 1950,
      "height": 2925,
      "urls": {
        "mobile": "https://image.tmdb.org/t/p/w342/aOIuZAjPaRIE74ryCFFn0zNfqFF.jpg",
        "tablet": "https://image.tmdb.org/t/p/w500/aOIuZAjPaRIE74ryCFFn0zNfqFF.jpg",
        "desktop": "https://image.tmdb.org/t/p/w780/aOIuZAjPaRIE74ryCFFn0zNfqFF.jpg",
        "tv": "https://image.tmdb.org/t/p/original/aOIuZAjPaRIE74ryCFFn0zNfqFF.jpg"
      }
    },
    {
      "file_path": "/hEpWvX6Bp79TmNfvSNGy4yOYqYt.jpg",
      "language": "de",
      "vote_average": 5.056,
      "width": 1000,
      "height": 1500,
      "urls": {
        "mobile": "https://image.tmdb.org/t/p/w342/hEpWvX6Bp79TmNfvSNGy4yOYqYt.jpg",
        "tablet": "https://image.tmdb.org/t/p/w500/hEpWvX6Bp79TmNfvSNGy4yOYqYt.jpg",
        "desktop": "https://image.tmdb.org/t/p/w780/hEpWvX6Bp79TmNfvSNGy4yOYqYt.jpg",
        "tv": "https://image.tmdb.org/t/p/original/hEpWvX6Bp79TmNfvSNGy4yOYqYt.jpg"
      }
    }
  ],
  "backdrops": [
    {
      "file_path": "/fNG7i7RqMErkcqhohV2a6cV1Ehy.jpg",
      "language": "en",
      "vote_average": 5.318,
      "width": 1920,
      "height": 1080,
      "urls": {
        "mobile": "https://image.tmdb.org/t/p/w300/fNG7i7RqMErkcqhohV2a6cV1Ehy.jpg",
        "tablet": "https://image.tmdb.org/t/p/w780/fNG7i7RqMErkcqhohV2a6cV1Ehy.jpg",
        "desktop": "https://image.tmdb.org/t/p/w1280/fNG7i7RqMErkcqhohV2a6cV1Ehy.jpg",
        "tv": "https://image.tmdb.org/t/p/original/fNG7i7RqMErkcqhohV2a6cV1Ehy.jpg"
      }
    },
    {
      "file_path": "/icmmSD4vTTDKOq2vvdulafOGw93.jpg",
      "language": "pt",
      "vote_average": 5.106,
      "width": 1920,
      "height": 1080,
      "urls": {
        "mobile": "https://image.tmdb.org/t/p/w300/icmmSD4vTTDKOq2vvdulafOGw93.jpg",
        "tablet": "https://image.tmdb.org/t/p/w780/icmmSD4vTTDKOq2vvdulafOGw93.jpg",
        "desktop": "https://image.tmdb.org/t/p/w1280/icmmSD4vTTDKOq2vvdulafOGw93.jpg",
        "tv": "https://image.tmdb.org/t/p/original/icmmSD4vTTDKOq2vvdulafOGw93.jpg"
      }
    },
    {
      "file_path": "/AbCwE5natLz26uhdLRlAXaUTdVH.jpg",
      "language": "es",
      "vote_average": 4.982,
      "width": 1920,
      "height": 1080,
      "urls": {
        "mobile": "https://image.tmdb.org/t/p/w300/AbCwE5natLz26uhdLRlAXaUTdVH.jpg",
        "tablet": "https://image.tmdb.org/t/p/w780/AbCwE5natLz26uhdLRlAXaUTdVH.jpg",
        "desktop": "https://image.tmdb.org/t/p/w1280/AbCwE5natLz26uhdLRlAXaUTdVH.jpg",
        "tv": "https://image.tmdb.org/t/p/original/AbCwE5natLz26uhdLRlAXaUTdVH.jpg"
      }
    }
  ]
}
```

**Exemplo - Série [SERIE] Breaking Bad (2008)/images.json**:

```json
{
  "id": 1396,
  "type": "tv",
  "title": "Breaking Bad",
  "original_title": "Breaking Bad",
  "release_date": "2008-01-20",
  "overview": "Um professor de química do ensino médio...",
  "year_from_sheet": "2008",
  "posters": [
    {
      "file_path": "/ggFHVNu6YYI5L9pCfOacjizRGt.jpg",
      "language": "en",
      "vote_average": 5.456,
      "width": 2000,
      "height": 3000,
      "urls": {
        "mobile": "https://image.tmdb.org/t/p/w342/ggFHVNu6YYI5L9pCfOacjizRGt.jpg",
        "tablet": "https://image.tmdb.org/t/p/w500/ggFHVNu6YYI5L9pCfOacjizRGt.jpg",
        "desktop": "https://image.tmdb.org/t/p/w780/ggFHVNu6YYI5L9pCfOacjizRGt.jpg",
        "tv": "https://image.tmdb.org/t/p/original/ggFHVNu6YYI5L9pCfOacjizRGt.jpg"
      }
    },
    {
      "file_path": "/30erzlzIOtOOap0pYd5kR2XXdcT.jpg",
      "language": "pt",
      "vote_average": 5.312,
      "width": 1000,
      "height": 1500,
      "urls": {
        "mobile": "https://image.tmdb.org/t/p/w342/30erzlzIOtOOap0pYd5kR2XXdcT.jpg",
        "tablet": "https://image.tmdb.org/t/p/w500/30erzlzIOtOOap0pYd5kR2XXdcT.jpg",
        "desktop": "https://image.tmdb.org/t/p/w780/30erzlzIOtOOap0pYd5kR2XXdcT.jpg",
        "tv": "https://image.tmdb.org/t/p/original/30erzlzIOtOOap0pYd5kR2XXdcT.jpg"
      }
    },
    {
      "file_path": "/ztkUQFLlC19CCMYHW9o1zWhJRNq.jpg",
      "language": "de",
      "vote_average": 5.246,
      "width": 2000,
      "height": 3000,
      "urls": {
        "mobile": "https://image.tmdb.org/t/p/w342/ztkUQFLlC19CCMYHW9o1zWhJRNq.jpg",
        "tablet": "https://image.tmdb.org/t/p/w500/ztkUQFLlC19CCMYHW9o1zWhJRNq.jpg",
        "desktop": "https://image.tmdb.org/t/p/w780/ztkUQFLlC19CCMYHW9o1zWhJRNq.jpg",
        "tv": "https://image.tmdb.org/t/p/original/ztkUQFLlC19CCMYHW9o1zWhJRNq.jpg"
      }
    }
  ],
  "backdrops": [
    {
      "file_path": "/tsRy63Mu5cu8etL1X7ZLyf7UP1M.jpg",
      "language": "en",
      "vote_average": 5.384,
      "width": 1920,
      "height": 1080,
      "urls": {
        "mobile": "https://image.tmdb.org/t/p/w300/tsRy63Mu5cu8etL1X7ZLyf7UP1M.jpg",
        "tablet": "https://image.tmdb.org/t/p/w780/tsRy63Mu5cu8etL1X7ZLyf7UP1M.jpg",
        "desktop": "https://image.tmdb.org/t/p/w1280/tsRy63Mu5cu8etL1X7ZLyf7UP1M.jpg",
        "tv": "https://image.tmdb.org/t/p/original/tsRy63Mu5cu8etL1X7ZLyf7UP1M.jpg"
      }
    },
    {
      "file_path": "/9faGSFi5jam6pDWGNd0p8JcJgXQ.jpg",
      "language": "pt",
      "vote_average": 5.252,
      "width": 1920,
      "height": 1080,
      "urls": {
        "mobile": "https://image.tmdb.org/t/p/w300/9faGSFi5jam6pDWGNd0p8JcJgXQ.jpg",
        "tablet": "https://image.tmdb.org/t/p/w780/9faGSFi5jam6pDWGNd0p8JcJgXQ.jpg",
        "desktop": "https://image.tmdb.org/t/p/w1280/9faGSFi5jam6pDWGNd0p8JcJgXQ.jpg",
        "tv": "https://image.tmdb.org/t/p/original/9faGSFi5jam6pDWGNd0p8JcJgXQ.jpg"
      }
    }
  ]
}
```

### 2. `all_content.json` (Consolidado)

Array com **todos** os filmes/séries processados. Útil para carregar tudo de uma vez.

**Estrutura**:

```json
[
  {
    "id": 603,
    "type": "movie",
    "title": "The Matrix",
    "original_title": "The Matrix",
    "release_date": "1999-03-30",
    "overview": "Thomas A. Anderson é um jovem programador...",
    "year_from_sheet": "1999",
    "posters": [ /* array de posters */ ],
    "backdrops": [ /* array de backdrops */ ]
  },
  {
    "id": 550,
    "type": "movie",
    "title": "Fight Club",
    "original_title": "Fight Club",
    "release_date": "1999-10-15",
    "overview": "Um funcionário de escritório insone...",
    "year_from_sheet": "1999",
    "posters": [ /* array de posters */ ],
    "backdrops": [ /* array de backdrops */ ]
  },
  {
    "id": 1396,
    "type": "tv",
    "title": "Breaking Bad",
    "original_title": "Breaking Bad",
    "release_date": "2008-01-20",
    "overview": "Um professor de química do ensino médio...",
    "year_from_sheet": "2008",
    "posters": [ /* array de posters */ ],
    "backdrops": [ /* array de backdrops */ ]
  }
]
```

## Campos Detalhados

### Metadados do Filme/Série

| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|---------|
| `id` | Integer | ID único do TMDB | `603` |
| `type` | String | Tipo de conteúdo | `"movie"` ou `"tv"` |
| `title` | String | Título em português (busca pt-BR) | `"Matrix"` |
| `original_title` | String | Título original | `"The Matrix"` |
| `release_date` | String | Data de lançamento (ISO 8601) | `"1999-03-30"` |
| `overview` | String | Sinopse em português | `"Thomas A. Anderson..."` |
| `year_from_sheet` | String/Null | Ano extraído da planilha | `"1999"` ou `null` |

### Campos de Cada Imagem (Poster/Backdrop)

| Campo | Tipo | Descrição | Exemplo | Uso |
|-------|------|-----------|---------|-----|
| `file_path` | String | Caminho único da imagem no TMDB | `"/qJ2tW6WMUDux911r6m7haRef0WH.jpg"` | Identificador único |
| `language` | String | Código ISO 639-1 do idioma | `"pt"`, `"en"`, `"es"` | Filtrar por idioma |
| `vote_average` | Float | Nota média da comunidade (0-10) | `5.384` | Ordenar por qualidade |
| `width` | Integer | Largura original em pixels | `2000` | Calcular aspect ratio |
| `height` | Integer | Altura original em pixels | `3000` | Layout responsivo |
| `urls` | Object | URLs para todas as resoluções | `{...}` | Uso direto |

### Objeto `urls` (Resoluções)

**Para Posters**:
```json
{
  "mobile": "https://image.tmdb.org/t/p/w342/path.jpg",
  "tablet": "https://image.tmdb.org/t/p/w500/path.jpg",
  "desktop": "https://image.tmdb.org/t/p/w780/path.jpg",
  "tv": "https://image.tmdb.org/t/p/original/path.jpg"
}
```

**Para Backdrops**:
```json
{
  "mobile": "https://image.tmdb.org/t/p/w300/path.jpg",
  "tablet": "https://image.tmdb.org/t/p/w780/path.jpg",
  "desktop": "https://image.tmdb.org/t/p/w1280/path.jpg",
  "tv": "https://image.tmdb.org/t/p/original/path.jpg"
}
```

## Endpoints TMDB Utilizados

### 1. Busca de Filme
```
GET /search/movie
```

**Exemplo**:
```
https://api.themoviedb.org/3/search/movie?api_key=XXX&query=Matrix&language=pt-BR&primary_release_year=1999
```

**Parâmetros**:
- `api_key`: Chave de API
- `query`: Título do filme
- `language`: pt-BR (para metadados em português)
- `primary_release_year`: Ano de lançamento (opcional)

### 2. Busca de Série
```
GET /search/tv
```

**Exemplo**:
```
https://api.themoviedb.org/3/search/tv?api_key=XXX&query=Breaking Bad&language=pt-BR&first_air_date_year=2008
```

**Parâmetros**:
- `api_key`: Chave de API
- `query`: Título da série
- `language`: pt-BR (para metadados em português)
- `first_air_date_year`: Ano de estreia (opcional)

### 3. Imagens do Filme/Série
```
GET /{type}/{id}/images
```

**Exemplo**:
```
https://api.themoviedb.org/3/movie/603/images?api_key=XXX
```

**Parâmetros**:
- `api_key`: Chave de API
- **SEM filtro de idioma** (busca todas as imagens)

**Observação**: A busca de imagens é feita **sem filtro de idioma** para depois aplicar o filtro programático que remove imagens com `iso_639_1 = null`.

## Instalação e Configuração

### Ambiente Virtual (Já Incluído)

O repositório já possui um ambiente virtual (`venv/`) com todas as dependências instaladas.

**Ativar venv**:

```bash
# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### Dependências

```
requests
```

Já instaladas no `venv/`. Não é necessário executar `pip install`.

### Configuração

No início do `main.py`:

```python
# Configuração
TMDB_API_KEY = "20c117664b56c63145516208a9dd5f5f"
GOOGLE_SHEET_ID = "1Mj8CovNSu03bpWnIGp_JntDUhxw5KjLRhbfqr8VfsHk"
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/"
OUTPUT_DIR = "/GitHub/Repos/Movie_Thumbnails/Images"

POSTER_SIZES = {
    "mobile": "w342",
    "tablet": "w500",
    "desktop": "w780",
    "tv": "original"
}

BACKDROP_SIZES = {
    "mobile": "w300",
    "tablet": "w780",
    "desktop": "w1280",
    "tv": "original"
}
```

## Execução

### Execução Manual

```bash
# Ativar venv
source venv/bin/activate

# Executar
python3 main.py
```

### Saída Detalhada

```
============================================================
🎬 TMDB URL Generator - Apenas imagens COM idioma
============================================================
📂 Diretório: /GitHub/Repos/Movie_Thumbnails/Images
❌ Filtrando imagens 'null' (sem texto)
============================================================

📊 Lendo planilha...
✅ Encontrados 150 itens

============================================================
Processando 150 itens...
============================================================

[1/150] The Matrix (1999)
------------------------------------------------------------
🔍 Buscando: The Matrix (1999)
   🎬 Tentando como FILME...
   ✅ FILME: The Matrix (1999) - ID: 603
   🌐 Buscando todas as imagens...
   🗑️  Removido: 3 posters + 2 backdrops sem texto
   📸 15 posters (8 idiomas)
   🖼️  12 backdrops (6 idiomas)
   🗣️  Idiomas: en, pt, es, fr, de, it, ja, ko
   🎨 Processando 15 posters...
   🎨 Processando 12 backdrops...
   ✅ Posters por idioma: {'de': 1, 'en': 5, 'es': 2, 'fr': 1, 'it': 1, 'ja': 2, 'ko': 1, 'pt': 2}
   ✅ Backdrops por idioma: {'en': 8, 'es': 2, 'pt': 2}
   💾 Salvo: /GitHub/Repos/Movie_Thumbnails/Images/The Matrix (1999)/images.json

[2/150] Inception (2010)
------------------------------------------------------------
🔍 Buscando: Inception (2010)
   🎬 Tentando como FILME...
   ✅ FILME: Inception (2010) - ID: 27205
   🌐 Buscando todas as imagens...
   🗑️  Removido: 5 posters + 3 backdrops sem texto
   📸 22 posters (12 idiomas)
   🖼️  18 backdrops (8 idiomas)
   🗣️  Idiomas: ar, cs, de, en, es, fr, hu, it, ja, ko, pt, zh
   🎨 Processando 22 posters...
   🎨 Processando 18 backdrops...
   ✅ Posters por idioma: {'ar': 1, 'cs': 1, 'de': 2, 'en': 6, 'es': 3, 'fr': 2, 'hu': 1, 'it': 1, 'ja': 1, 'ko': 1, 'pt': 2, 'zh': 1}
   ✅ Backdrops por idioma: {'de': 1, 'en': 12, 'es': 2, 'fr': 1, 'it': 1, 'pt': 1}
   💾 Salvo: /GitHub/Repos/Movie_Thumbnails/Images/Inception (2010)/images.json

[3/150] Breaking Bad (2008)
------------------------------------------------------------
🔍 Buscando: Breaking Bad (2008)
   🎬 Tentando como FILME...
   📺 Tentando como SÉRIE...
   ✅ SÉRIE: Breaking Bad (2008) - ID: 1396
   🌐 Buscando todas as imagens...
   🗑️  Removido: 2 posters + 1 backdrops sem texto
   📸 18 posters (9 idiomas)
   🖼️  15 backdrops (5 idiomas)
   🗣️  Idiomas: de, en, es, fr, hu, it, ko, pt, ru
   🎨 Processando 18 posters...
   🎨 Processando 15 backdrops...
   ✅ Posters por idioma: {'de': 2, 'en': 6, 'es': 2, 'fr': 1, 'hu': 1, 'it': 1, 'ko': 1, 'pt': 3, 'ru': 1}
   ✅ Backdrops por idioma: {'en': 10, 'es': 2, 'fr': 1, 'pt': 2}
   💾 Salvo: /GitHub/Repos/Movie_Thumbnails/Images/[SERIE] Breaking Bad (2008)/images.json

...

============================================================
✅ CONCLUÍDO!
============================================================
📊 Processados: 148/150

📺 POR TIPO:
   🎬 Filmes: 120
   📺 Séries: 28

⚠️  PULADOS (2):
   • Film Not Found (2025)
   • Another Missing Title (2020)

📊 IMAGENS:
   Total de posters: 2340
   Total de backdrops: 1856
   Total de imagens: 4196
   Idiomas únicos: 42
   🗣️  ar, bg, cn, cs, da, de, el, en, es, fa, fi, fr, he, hi, hr, hu, id, it, ja, ko, lt, nl, no, pl, pt, ro, ru, sk, sl, sr, sv, th, tr, uk, vi, zh, ... (+6)
   💾 /GitHub/Repos/Movie_Thumbnails/Images/all_content.json

============================================================
```

## Configuração como Serviço Systemd

O repositório inclui `movie-thumbnails.service`.

**Configurar**:

```bash
# Criar link simbólico
sudo ln -s /caminho/absoluto/Movie_Thumbnails/movie-thumbnails.service /etc/systemd/system/

# Recarregar daemon
sudo systemctl daemon-reload

# Habilitar no boot
sudo systemctl enable movie-thumbnails

# Iniciar serviço
sudo systemctl start movie-thumbnails
```

**Gerenciar**:

```bash
# Verificar status
sudo systemctl status movie-thumbnails

# Ver logs em tempo real
sudo journalctl -u movie-thumbnails -f

# Ver últimas 100 linhas
sudo journalctl -u movie-thumbnails -n 100

# Parar serviço
sudo systemctl stop movie-thumbnails

# Reiniciar serviço
sudo systemctl restart movie-thumbnails
```

## Exemplos de Uso

### 1. Carregar JSON Individual

```python
import json

# Carregar imagens do The Matrix
with open('Images/The Matrix (1999)/images.json', 'r', encoding='utf-8') as f:
    matrix = json.load(f)

print(f"ID TMDB: {matrix['id']}")
print(f"Tipo: {matrix['type']}")
print(f"Título: {matrix['title']}")
print(f"Total de posters: {len(matrix['posters'])}")
print(f"Total de backdrops: {len(matrix['backdrops'])}")
```

### 2. Selecionar Melhor Poster por Idioma

```python
import json

with open('Images/The Matrix (1999)/images.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Filtrar posters em português
pt_posters = [p for p in data['posters'] if p['language'] == 'pt']

# Ordenar por qualidade (vote_average)
pt_posters_sorted = sorted(pt_posters, key=lambda x: x['vote_average'], reverse=True)

# Pegar o melhor
best_poster = pt_posters_sorted[0]

print(f"Melhor poster PT:")
print(f"  Qualidade: {best_poster['vote_average']}")
print(f"  Resolução: {best_poster['width']}x{best_poster['height']}")
print(f"  URL Desktop: {best_poster['urls']['desktop']}")
```

**Saída**:
```
Melhor poster PT:
  Qualidade: 5.252
  Resolução: 1382x2048
  URL Desktop: https://image.tmdb.org/t/p/w780/dXNAPwY7VrqMAo51EKhhCJfaGb5.jpg
```

### 3. Listar Idiomas Disponíveis

```python
import json

with open('Images/The Matrix (1999)/images.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Coletar idiomas únicos
languages = set()
for poster in data['posters']:
    languages.add(poster['language'])
for backdrop in data['backdrops']:
    languages.add(backdrop['language'])

print(f"Idiomas disponíveis ({len(languages)}): {sorted(languages)}")
```

**Saída**:
```
Idiomas disponíveis (8): ['de', 'en', 'es', 'fr', 'it', 'ja', 'ko', 'pt']
```

### 4. Carregar Todos os Filmes/Séries

```python
import json

# Carregar arquivo consolidado
with open('Images/all_content.json', 'r', encoding='utf-8') as f:
    all_content = json.load(f)

# Estatísticas
movies = [c for c in all_content if c['type'] == 'movie']
series = [c for c in all_content if c['type'] == 'tv']

print(f"Total de itens: {len(all_content)}")
print(f"Filmes: {len(movies)}")
print(f"Séries: {len(series)}")

# Buscar filme específico por ID
matrix = next((c for c in all_content if c['id'] == 603), None)
if matrix:
    print(f"
The Matrix:")
    print(f"  {len(matrix['posters'])} posters")
    print(f"  {len(matrix['backdrops'])} backdrops")
```

### 5. Filtrar Imagens HD

```python
import json

with open('Images/Inception (2010)/images.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Filtrar posters com resolução >= 1920px
hd_posters = [p for p in data['posters'] if p['width'] >= 1920]

print(f"Posters HD (>= 1920px): {len(hd_posters)}")
for p in hd_posters:
    print(f"  {p['language']}: {p['width']}x{p['height']} - Nota: {p['vote_average']}")
```

### 6. Estatísticas por Idioma

```python
import json
from collections import Counter

with open('Images/Breaking Bad (2008)/images.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Contar posters por idioma
poster_langs = [p['language'] for p in data['posters']]
poster_count = Counter(poster_langs)

# Contar backdrops por idioma
backdrop_langs = [b['language'] for b in data['backdrops']]
backdrop_count = Counter(backdrop_langs)

print("Posters por idioma:")
for lang, count in poster_count.most_common():
    print(f"  {lang}: {count}")

print("
Backdrops por idioma:")
for lang, count in backdrop_count.most_common():
    print(f"  {lang}: {count}")
```

## Uso Responsivo em Web

### HTML5 Picture Element

```html
<!-- Poster responsivo -->
<picture>
  <source media="(max-width: 480px)" 
          srcset="https://image.tmdb.org/t/p/w342/qJ2tW6WMUDux911r6m7haRef0WH.jpg">
  <source media="(max-width: 768px)" 
          srcset="https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg">
  <source media="(max-width: 1920px)" 
          srcset="https://image.tmdb.org/t/p/w780/qJ2tW6WMUDux911r6m7haRef0WH.jpg">
  <img src="https://image.tmdb.org/t/p/original/qJ2tW6WMUDux911r6m7haRef0WH.jpg" 
       alt="The Matrix Poster"
       loading="lazy">
</picture>

<!-- Backdrop responsivo -->
<picture>
  <source media="(max-width: 480px)" 
          srcset="https://image.tmdb.org/t/p/w300/fNG7i7RqMErkcqhohV2a6cV1Ehy.jpg">
  <source media="(max-width: 1024px)" 
          srcset="https://image.tmdb.org/t/p/w780/fNG7i7RqMErkcqhohV2a6cV1Ehy.jpg">
  <source media="(max-width: 1920px)" 
          srcset="https://image.tmdb.org/t/p/w1280/fNG7i7RqMErkcqhohV2a6cV1Ehy.jpg">
  <img src="https://image.tmdb.org/t/p/original/fNG7i7RqMErkcqhohV2a6cV1Ehy.jpg" 
       alt="The Matrix Backdrop"
       loading="lazy">
</picture>
```

### CSS Background

```css
.hero-section {
  background-image: url('https://image.tmdb.org/t/p/w1280/fNG7i7RqMErkcqhohV2a6cV1Ehy.jpg');
  background-size: cover;
  background-position: center;
  height: 500px;
}

@media (max-width: 1024px) {
  .hero-section {
    background-image: url('https://image.tmdb.org/t/p/w780/fNG7i7RqMErkcqhohV2a6cV1Ehy.jpg');
  }
}

@media (max-width: 768px) {
  .hero-section {
    background-image: url('https://image.tmdb.org/t/p/w300/fNG7i7RqMErkcqhohV2a6cV1Ehy.jpg');
    height: 300px;
  }
}
```

### React Component

```jsx
import React from 'react';
import imageData from './Images/The Matrix (1999)/images.json';

function MoviePoster({ language = 'pt', quality = 'best' }) {
  // Filtrar por idioma
  const posters = imageData.posters.filter(p => p.language === language);

  if (!posters.length) return null;

  // Ordenar por qualidade
  const sorted = posters.sort((a, b) => b.vote_average - a.vote_average);
  const poster = sorted[0];

  return (
    <div className="movie-poster">
      <img
        src={poster.urls.desktop}
        srcSet={`
          ${poster.urls.mobile} 480w,
          ${poster.urls.tablet} 768w,
          ${poster.urls.desktop} 1024w,
          ${poster.urls.tv} 1920w
        `}
        sizes="(max-width: 480px) 342px, (max-width: 768px) 500px, (max-width: 1024px) 780px, 100vw"
        alt={imageData.title}
        loading="lazy"
      />
      <p>Qualidade: {poster.vote_average.toFixed(2)}/10</p>
    </div>
  );
}

export default MoviePoster;
```

### Next.js

```jsx
import Image from 'next/image';
import imageData from '@/data/Images/The Matrix (1999)/images.json';

export default function MovieCard() {
  const poster = imageData.posters
    .filter(p => p.language === 'pt')
    .sort((a, b) => b.vote_average - a.vote_average)[0];

  return (
    <div className="movie-card">
      <Image
        src={poster.urls.desktop}
        alt={imageData.title}
        width={poster.width}
        height={poster.height}
        sizes="(max-width: 480px) 342px, (max-width: 768px) 500px, (max-width: 1024px) 780px, 100vw"
        quality={85}
        priority
      />
      <h2>{imageData.title}</h2>
      <p>{imageData.overview}</p>
    </div>
  );
}
```

### Vue.js

```vue
<template>
  <div class="movie-gallery">
    <h1>{{ movie.title }}</h1>

    <div class="posters">
      <picture v-for="poster in topPosters" :key="poster.file_path">
        <source
          :srcset="poster.urls.mobile"
          media="(max-width: 480px)"
        />
        <source
          :srcset="poster.urls.tablet"
          media="(max-width: 768px)"
        />
        <source
          :srcset="poster.urls.desktop"
          media="(max-width: 1920px)"
        />
        <img
          :src="poster.urls.tv"
          :alt="`${movie.title} - ${poster.language}`"
          loading="lazy"
        />
      </picture>
    </div>
  </div>
</template>

<script>
import imageData from './Images/The Matrix (1999)/images.json';

export default {
  data() {
    return {
      movie: imageData
    };
  },
  computed: {
    topPosters() {
      return this.movie.posters
        .sort((a, b) => b.vote_average - a.vote_average)
        .slice(0, 5);
    }
  }
};
</script>
```

## Nomenclatura de Pastas

### Filmes

```
The Matrix (1999)/
  └── images.json

Inception (2010)/
  └── images.json

Fight Club (1999)/
  └── images.json

Interstellar (2014)/
  └── images.json
```

### Séries (Prefixo `[SERIE]`)

```
[SERIE] Breaking Bad (2008)/
  └── images.json

[SERIE] Game of Thrones (2011)/
  └── images.json

[SERIE] The Office (2005)/
  └── images.json

[SERIE] Stranger Things (2016)/
  └── images.json
```

## Idiomas Suportados

O sistema captura imagens em **todos os idiomas** que possuem `iso_639_1` definido.

### Idiomas Mais Comuns

| Código | Idioma | Nome Nativo |
|--------|--------|-------------|
| en | English | English |
| pt | Portuguese | Português |
| es | Spanish | Español |
| fr | French | Français |
| de | German | Deutsch |
| it | Italian | Italiano |
| ja | Japanese | 日本語 |
| ko | Korean | 한국어 |
| zh | Chinese | 中文 |
| ru | Russian | Русский |
| ar | Arabic | العربية |
| hi | Hindi | हिन्दी |
| th | Thai | ไทย |
| tr | Turkish | Türkçe |
| pl | Polish | Polski |
| nl | Dutch | Nederlands |
| sv | Swedish | Svenska |
| no | Norwegian | Norsk |
| da | Danish | Dansk |
| fi | Finnish | Suomi |

### Outros Idiomas

cs, hu, ro, el, he, vi, id, uk, bg, hr, sr, sk, sl, lt, lv, et, fa, ms, bn, ta, te, ml, kn, mr, gu, pa, ur, e muitos outros.

## Tratamento de Erros

### Item não encontrado

**Saída**:
```
🔍 Buscando: Film Not Found (2025)
   🎬 Tentando como FILME...
   📺 Tentando como SÉRIE...
   ⚠️  Não encontrado com ano 2025
   🔄 Tentando sem ano...
   ❌ Não encontrado
   ⏭️  PULADO
```

**Causa**: Título não existe no TMDB ou ano incorreto  
**Solução**: Verificar planilha e ajustar título/ano

### Sem imagens COM idioma

**Saída**:
```
🌐 Buscando todas as imagens...
🗑️  Removido: 8 posters + 6 backdrops sem texto
📸 0 posters (0 idiomas)
🖼️  0 backdrops (0 idiomas)
⚠️  Nenhuma imagem COM idioma encontrada!
⏭️  PULADO
```

**Causa**: TMDB só tem imagens sem texto (null)  
**Solução**: Normal para filmes antigos/obscuros

### Timeout

**Saída**:
```
❌ Erro: HTTPConnectionPool(...): Read timed out
```

**Causa**: Conexão lenta ou API instável  
**Solução**: Aumentar timeout no código ou aguardar

### Interrupção Manual

**Comportamento**:
```
^C
⚠️  Interrompido
```

- JSONs individuais já salvos permanecem
- `all_content.json` só é gerado no final
- Reexecutar reprocessa tudo

## Performance

### Timeouts

```python
# Busca (search)
response = requests.get(url, params=params, timeout=10)

# Imagens (maior volume)
response = requests.get(url, params=params, timeout=20)
```

### Processamento

- **Sequencial**: Um item por vez
- **Sem rate limiting explícito**
- **Sem cache**: Sempre busca fresco do TMDB

### Otimizações Possíveis

**1. Implementar cache local**:
```python
import os, json
from datetime import datetime, timedelta

def get_cached(item_id, max_age_days=7):
    cache_file = f"cache/{item_id}.json"
    if os.path.exists(cache_file):
        age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache_file))
        if age < timedelta(days=max_age_days):
            with open(cache_file) as f:
                return json.load(f)
    return None
```

**2. Adicionar rate limiting**:
```python
import time

# Entre requisições
time.sleep(0.25)  # 4 req/s
```

**3. Processamento paralelo**:
```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    executor.map(process_item, items)
```

## Recursos da API

- **TMDB API Docs**: https://developers.themoviedb.org/3
- **Images Endpoint**: https://developers.themoviedb.org/3/movies/get-movie-images
- **Image Sizing**: https://developers.themoviedb.org/3/getting-started/images
- **Configuration**: https://developers.themoviedb.org/3/configuration/get-api-configuration

## Notas Importantes

- ✅ **Filtra imagens null**: Remove imagens sem `iso_639_1` (sem texto)
- ✅ **4 resoluções**: mobile, tablet, desktop, tv
- ✅ **URLs prontas**: Direto do CDN TMDB (não requer download)
- ✅ **JSON por pasta**: Organização individual
- ✅ **JSON consolidado**: all_content.json com tudo
- ✅ **Prefixo [SERIE]**: Facilita identificação
- ✅ **vote_average**: Métrica de qualidade da comunidade
- ✅ **Metadados completos**: width, height, language
- ✅ **Busca inteligente**: Filme → Série → Sem ano
- ✅ **Estatísticas**: Contagem por idioma e tipo
