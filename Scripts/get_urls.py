#!/usr/bin/env python3
"""
TMDB URL Generator - SEM imagens null
Pega todas as imagens COM idioma (remove imagens sem texto)
"""

import requests
import os
import json
import csv
import re

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

print("=" * 60)
print("🎬 TMDB URL Generator - Apenas imagens COM idioma")
print("=" * 60)
print(f"📂 Diretório: {OUTPUT_DIR}")
print(f"❌ Filtrando imagens 'null' (sem texto)")
print("=" * 60)
print()


def parse_title_and_year(text):
    """Extrai título e ano"""
    match = re.match(r'^(.+?)\s*\((\d{4})\)\s*$', text)
    if match:
        return match.group(1).strip(), match.group(2)

    match = re.match(r'^(.+?)\s*-\s*(\d{4})\s*$', text)
    if match:
        return match.group(1).strip(), match.group(2)

    return text.strip(), None


def read_movies_from_sheet():
    """Lê planilha"""
    print("📊 Lendo planilha...")
    try:
        csv_url = f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/export?format=csv&gid=0"
        response = requests.get(csv_url, timeout=10)
        response.raise_for_status()

        lines = response.text.strip().split('\n')
        reader = csv.reader(lines)

        items = []
        for i, row in enumerate(reader):
            if i == 0:
                continue
            if row and row[0].strip():
                text = row[0].strip()
                title, year = parse_title_and_year(text)
                items.append({
                    "title": title,
                    "year": year,
                    "original": text
                })

        print(f"✅ Encontrados {len(items)} itens\n")
        return items
    except Exception as e:
        print(f"❌ Erro ao ler planilha: {e}")
        return []


def search_movie(title, year=None):
    """Busca FILME"""
    try:
        url = f"{TMDB_BASE_URL}/search/movie"
        params = {
            "api_key": TMDB_API_KEY,
            "query": title,
            "language": "pt-BR"
        }

        if year:
            params["primary_release_year"] = year

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("results"):
            result = data["results"][0]
            release_year = result.get("release_date", "")[:4]

            if year and release_year != year:
                return None

            return {
                "id": result["id"],
                "type": "movie",
                "title": result["title"],
                "original_title": result.get("original_title", ""),
                "release_date": result.get("release_date", ""),
                "overview": result.get("overview", ""),
                "year": release_year
            }

        return None
    except Exception as e:
        return None


def search_tv(title, year=None):
    """Busca SÉRIE"""
    try:
        url = f"{TMDB_BASE_URL}/search/tv"
        params = {
            "api_key": TMDB_API_KEY,
            "query": title,
            "language": "pt-BR"
        }

        if year:
            params["first_air_date_year"] = year

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("results"):
            result = data["results"][0]
            first_air_year = result.get("first_air_date", "")[:4]

            if year and first_air_year != year:
                return None

            return {
                "id": result["id"],
                "type": "tv",
                "title": result["name"],
                "original_title": result.get("original_name", ""),
                "release_date": result.get("first_air_date", ""),
                "overview": result.get("overview", ""),
                "year": first_air_year
            }

        return None
    except Exception as e:
        return None


def search_content(title, year=None):
    """Busca FILME ou SÉRIE"""
    if year:
        print(f"🔍 Buscando: {title} ({year})")
    else:
        print(f"🔍 Buscando: {title}")

    print(f"   🎬 Tentando como FILME...")
    movie = search_movie(title, year)
    if movie:
        print(f"   ✅ FILME: {movie['title']} ({movie['year']}) - ID: {movie['id']}")
        return movie

    print(f"   📺 Tentando como SÉRIE...")
    tv = search_tv(title, year)
    if tv:
        print(f"   ✅ SÉRIE: {tv['title']} ({tv['year']}) - ID: {tv['id']}")
        return tv

    if year:
        print(f"   ⚠️  Não encontrado com ano {year}")
        print(f"   🔄 Tentando sem ano...")

        movie = search_movie(title, None)
        if movie:
            print(f"   ⚠️  FILME: {movie['title']} ({movie['year']})")
            print(f"   ❌ Ano não bate (esperado: {year}, encontrado: {movie['year']})")
            return None

        tv = search_tv(title, None)
        if tv:
            print(f"   ⚠️  SÉRIE: {tv['title']} ({tv['year']})")
            print(f"   ❌ Ano não bate (esperado: {year}, encontrado: {tv['year']})")
            return None

    print(f"   ❌ Não encontrado")
    return None


def get_images(content_id, content_type):
    """
    Obtém TODAS as imagens e FILTRA as que não têm idioma (null)
    """
    try:
        url = f"{TMDB_BASE_URL}/{content_type}/{content_id}/images"

        # Sem filtro de idioma para pegar todas
        params = {
            "api_key": TMDB_API_KEY
        }

        print(f"   🌐 Buscando todas as imagens...")

        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()

        all_posters = data.get("posters", [])
        all_backdrops = data.get("backdrops", [])

        # FILTRAR: Remover imagens sem idioma (null)
        posters = [p for p in all_posters if p.get("iso_639_1") is not None]
        backdrops = [b for b in all_backdrops if b.get("iso_639_1") is not None]

        # Estatísticas
        removed_posters = len(all_posters) - len(posters)
        removed_backdrops = len(all_backdrops) - len(backdrops)

        if removed_posters > 0 or removed_backdrops > 0:
            print(f"   🗑️  Removido: {removed_posters} posters + {removed_backdrops} backdrops sem texto")

        # Contar idiomas únicos
        poster_langs = set(p.get("iso_639_1") for p in posters)
        backdrop_langs = set(b.get("iso_639_1") for b in backdrops)

        print(f"   📸 {len(posters)} posters ({len(poster_langs)} idiomas)")
        print(f"   🖼️  {len(backdrops)} backdrops ({len(backdrop_langs)} idiomas)")

        if poster_langs:
            langs_list = sorted(list(poster_langs))
            if len(langs_list) <= 10:
                print(f"   🗣️  Idiomas: {', '.join(langs_list)}")
            else:
                sample = ', '.join(langs_list[:10])
                print(f"   🗣️  Idiomas: {sample}, ... (+{len(langs_list)-10} mais)")

        return posters, backdrops
    except Exception as e:
        print(f"   ❌ Erro ao obter imagens: {e}")
        import traceback
        traceback.print_exc()
        return [], []


def generate_urls(file_path, sizes_dict):
    """Gera URLs"""
    urls = {}
    for device, size in sizes_dict.items():
        urls[device] = f"{TMDB_IMAGE_BASE}{size}{file_path}"
    return urls


def process_item(item_info):
    """Processa um item"""
    title = item_info["title"]
    year = item_info["year"]

    content = search_content(title, year)
    if not content:
        return None

    posters, backdrops = get_images(content["id"], content["type"])

    if not posters and not backdrops:
        print(f"   ⚠️  Nenhuma imagem COM idioma encontrada!")
        return None

    content_data = {
        "id": content["id"],
        "type": content["type"],
        "title": content["title"],
        "original_title": content["original_title"],
        "release_date": content["release_date"],
        "overview": content["overview"],
        "year_from_sheet": year,
        "posters": [],
        "backdrops": []
    }

    # Processar posters
    print(f"   🎨 Processando {len(posters)} posters...")
    for poster in posters:
        urls = generate_urls(poster["file_path"], POSTER_SIZES)
        language = poster.get("iso_639_1")
        content_data["posters"].append({
            "file_path": poster["file_path"],
            "language": language,
            "vote_average": poster.get("vote_average", 0),
            "width": poster.get("width", 0),
            "height": poster.get("height", 0),
            "urls": urls
        })

    # Processar backdrops
    print(f"   🎨 Processando {len(backdrops)} backdrops...")
    for backdrop in backdrops:
        urls = generate_urls(backdrop["file_path"], BACKDROP_SIZES)
        language = backdrop.get("iso_639_1")
        content_data["backdrops"].append({
            "file_path": backdrop["file_path"],
            "language": language,
            "vote_average": backdrop.get("vote_average", 0),
            "width": backdrop.get("width", 0),
            "height": backdrop.get("height", 0),
            "urls": urls
        })

    # Estatísticas por idioma
    poster_by_lang = {}
    for p in content_data["posters"]:
        lang = p["language"]
        poster_by_lang[lang] = poster_by_lang.get(lang, 0) + 1

    backdrop_by_lang = {}
    for b in content_data["backdrops"]:
        lang = b["language"]
        backdrop_by_lang[lang] = backdrop_by_lang.get(lang, 0) + 1

    print(f"   ✅ Posters por idioma: {dict(sorted(poster_by_lang.items()))}")
    print(f"   ✅ Backdrops por idioma: {dict(sorted(backdrop_by_lang.items()))}")

    return content_data


def main():
    """Função principal"""

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    items = read_movies_from_sheet()

    if not items:
        print("\n❌ Nenhum item encontrado!")
        return

    print(f"{'=' * 60}")
    print(f"Processando {len(items)} itens...")
    print(f"{'=' * 60}\n")

    all_content_data = []
    skipped = []

    for i, item_info in enumerate(items, 1):
        display_name = item_info["original"]
        print(f"[{i}/{len(items)}] {display_name}")
        print("-" * 60)

        try:
            content_data = process_item(item_info)
            if content_data:
                all_content_data.append(content_data)

                # Nome da pasta
                safe_name = "".join(c for c in content_data["title"] if c.isalnum() or c in (' ', '-', '_')).strip()

                if item_info["year"]:
                    safe_name = f"{safe_name} ({item_info['year']})"
                else:
                    year = content_data["release_date"][:4] if content_data["release_date"] else ""
                    if year:
                        safe_name = f"{safe_name} ({year})"

                if content_data["type"] == "tv":
                    safe_name = f"[SERIE] {safe_name}"

                content_dir = os.path.join(OUTPUT_DIR, safe_name)
                os.makedirs(content_dir, exist_ok=True)

                json_path = os.path.join(content_dir, "images.json")
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(content_data, f, indent=2, ensure_ascii=False)

                print(f"   💾 Salvo: {json_path}")
            else:
                skipped.append(item_info["original"])
                print(f"   ⏭️  PULADO")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            skipped.append(item_info["original"])
            import traceback
            traceback.print_exc()

        print()

    # Salvar JSON consolidado
    consolidated_path = os.path.join(OUTPUT_DIR, "all_content.json")
    with open(consolidated_path, 'w', encoding='utf-8') as f:
        json.dump(all_content_data, f, indent=2, ensure_ascii=False)

    print(f"{'=' * 60}")
    print(f"✅ CONCLUÍDO!")
    print(f"{'=' * 60}")
    print(f"📊 Processados: {len(all_content_data)}/{len(items)}")

    # Estatísticas
    movies_count = sum(1 for c in all_content_data if c["type"] == "movie")
    tv_count = sum(1 for c in all_content_data if c["type"] == "tv")

    print(f"\n📺 POR TIPO:")
    print(f"   🎬 Filmes: {movies_count}")
    print(f"   📺 Séries: {tv_count}")

    if skipped:
        print(f"\n⚠️  PULADOS ({len(skipped)}):")
        for s in skipped[:5]:
            print(f"   • {s}")
        if len(skipped) > 5:
            print(f"   ... (+{len(skipped)-5})")

    if all_content_data:
        total_posters = sum(len(c["posters"]) for c in all_content_data)
        total_backdrops = sum(len(c["backdrops"]) for c in all_content_data)

        # Contar idiomas únicos
        all_langs = set()
        for c in all_content_data:
            for p in c["posters"]:
                all_langs.add(p["language"])
            for b in c["backdrops"]:
                all_langs.add(b["language"])

        print(f"\n📊 IMAGENS:")
        print(f"   Total de posters: {total_posters}")
        print(f"   Total de backdrops: {total_backdrops}")
        print(f"   Total de imagens: {total_posters + total_backdrops}")
        print(f"   Idiomas únicos: {len(all_langs)}")

        if all_langs:
            langs_sorted = sorted(list(all_langs))
            if len(langs_sorted) <= 20:
                print(f"   🗣️  {', '.join(langs_sorted)}")
            else:
                sample = ', '.join(langs_sorted[:20])
                print(f"   🗣️  {sample}, ... (+{len(langs_sorted)-20})")

        print(f"   💾 {consolidated_path}")

    print(f"\n{'=' * 60}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompido")
    except Exception as e:
        print(f"\n\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
