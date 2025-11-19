# Movie_Thumbnails

Serviço Python automatizado para extração de URLs de pôsteres e banners de filmes/séries em múltiplas resoluções e idiomas via TMDB API, **excluindo imagens sem texto** e organizando em **subpastas por collections e temporadas**.

## Visão Geral

O Movie_Thumbnails lê títulos de filmes/séries de uma planilha Google Sheets, busca cada item no TMDB usando **Collections** (franquias) ou **Multi-search** e extrai **todas as imagens COM idioma** (pôsteres e backdrops), filtrando programaticamente imagens internacionais sem texto (`iso_639_1 = null`). Gera URLs para múltiplas resoluções otimizadas para uso responsivo em web.

## Funcionalidades Principais

### Busca Inteligente

- **Collections Automáticas**: Detecta automaticamente franquias (James Bond, Harry Potter, Fast & Furious, etc.)
- **Multi-search**: Busca simultânea em filmes e séries com ordenação por popularidade
- **Popularidade Mínima**: Filtra resultados com popularidade >= 5.0
- **Similaridade de Título**: Valida títulos com mínimo de 60% de similaridade (desabilitado em buscas gerais)
- **Suporte a Temporadas**: Extrai imagens específicas de temporadas de séries

### Formatos de Input Suportados

| Formato | Descrição | Exemplo | Resultado |
|---------|-----------|---------|-----------|
| `Nome` | Busca collection primeiro, senão todas as versões | `James Bond` | Toda a collection (25+ filmes) |
| `Nome - YYYY` | Filme específico do ano | `Batman - 2022` | Apenas The Batman (2022) |
| `Nome - s1` | Série, temporada 1 | `Severance - s1` | Temporada 1 de Severance |
| `Nome - s` | Série, todas as temporadas | `Breaking Bad - s` | Todas as 5 temporadas |

### Estrutura de Pastas Organizada

```
Images/
├── James Bond Collection/
│   ├── Casino Royale (2006)/
│   │   └── images.json
│   ├── Skyfall (2012)/
│   │   └── images.json
│   └── No Time to Die (2021)/
│       └── images.json
├── [SERIE] Severance/
│   ├── Season 1/
│   │   └── images.json
│   └── Season 2/
│       └── images.json
├── The Batman (2022)/
│   └── images.json
└── all_content.json
```

### Filtro Inteligente de Imagens

**DIFERENCIAL**: O sistema busca **TODAS as imagens** via API do TMDB (sem filtro de idioma) e então **filtra programaticamente** apenas as imagens que possuem `iso_639_1` (código de idioma) definido.

```python
# Filtro aplicado no código:
posters = [p for p in all_posters if p.get("iso_639_1") is not None]
backdrops = [b for b in all_backdrops if b.get("iso_639_1") is not None]
```

### Resoluções Disponíveis

#### Pôsteres (Posters)

| Device | Largura | Tamanho TMDB |
|--------|---------|--------------|
| Mobile | 342px | `w342` |
| Tablet | 500px | `w500` |
| Desktop | 780px | `w780` |
| TV | Original | `original` |

#### Banners (Backdrops)

| Device | Largura | Tamanho TMDB |
|--------|---------|--------------|
| Mobile | 300px | `w300` |
| Tablet | 780px | `w780` |
| Desktop | 1280px | `w1280` |
| TV | Original | `original` |

## Configuração

```python
TMDB_API_KEY = "sua_api_key"
GOOGLE_SHEET_ID = "seu_sheet_id"
OUTPUT_DIR = "/caminho/para/output"
MIN_POPULARITY = 5.0
MIN_TITLE_SIMILARITY = 0.6
```

## Endpoints TMDB Utilizados

1. **`/search/collection`** - Busca de collections (franquias)
2. **`/collection/{id}`** - Detalhes e filmes da collection
3. **`/search/multi`** - Busca combinada de filmes e séries
4. **`/tv/{id}`** - Detalhes da série (lista de temporadas)
5. **`/tv/{id}/season/{season}/images`** - Imagens de temporada específica
6. **`/{type}/{id}/images`** - Imagens gerais (sem filtro de idioma)

## Instalação do Serviço Systemd

Para configurar o serviço para rodar automaticamente:

```bash
# 1. Criar link simbólico do arquivo de serviço
sudo ln -s /caminho/para/repositorio/Services/movie-thumbnails.service /etc/systemd/system/

# 2. Recarregar daemon do systemd
sudo systemctl daemon-reload

# 3. Habilitar serviço para iniciar no boot
sudo systemctl enable movie-thumbnails.service

# 4. Iniciar serviço
sudo systemctl start movie-thumbnails.service

# 5. Verificar status
sudo systemctl status movie-thumbnails.service
```

## Execução Manual

```bash
# Ativar venv
source venv/bin/activate

# Executar
python3 main.py
```
