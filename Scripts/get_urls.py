#!/usr/bin/env python3
"""
TMDB URL Generator - Collections + Subpastas Organizadas
"""

import requests
import os
import json
import csv
import re
from difflib import SequenceMatcher

TMDB_API_KEY = "20c117664b56c63145516208a9dd5f5f"
GOOGLE_SHEET_ID = "1Mj8CovNSu03bpWnIGp_JntDUhxw5KjLRhbfqr8VfsHk"
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/"
OUTPUT_DIR = "/GitHub/Repos/Movie_Thumbnails/Images"

MIN_POPULARITY = 5.0
MIN_TITLE_SIMILARITY = 0.6

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
print("🎬 TMDB URL Generator - Organizando em Subpastas")
print("=" * 60)
print(f"📂 Diretório: {OUTPUT_DIR}")
print("=" * 60)
print()

def title_similarity(a, b):
    """Calcula similaridade entre dois títulos"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def parse_input(text):
    """Parse inputs"""
    # Série com temporada
    match = re.match(r'^(.+?)\s*-\s*s(\d+)?\s*$', text, re.IGNORECASE)
    if match:
        title = match.group(1).strip()
        season_str = match.group(2)
        season = int(season_str) if season_str else "all"
        return title, None, season
    
    # Filme
    match = re.match(r'^(.+?)\s*-\s*(\d{4})\s*$', text)
    if match:
        return match.group(1).strip(), match.group(2), None
    
    return text.strip(), None, None

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
                title, year, season = parse_input(text)
                items.append({
                    "title": title,
                    "year": year,
                    "season": season,
                    "original": text
                })
        
        print(f"✅ Encontrados {len(items)} itens\n")
        return items
    except Exception as e:
        print(f"❌ Erro ao ler planilha: {e}")
        return []

def search_collection(title):
    """Busca collection"""
    try:
        url = f"{TMDB_BASE_URL}/search/collection"
        params = {
            "api_key": TMDB_API_KEY,
            "query": title,
            "language": "en-US"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("results"):
            return None, None
        
        results = sorted(data["results"], key=lambda x: x.get("popularity", 0), reverse=True)
        collection = results[0]
        return collection.get("id"), collection.get("name")
        
    except Exception as e:
        return None, None

def get_collection_movies(collection_id):
    """Pega filmes da collection"""
    try:
        url = f"{TMDB_BASE_URL}/collection/{collection_id}"
        params = {"api_key": TMDB_API_KEY, "language": "en-US"}
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        parts = data.get("parts", [])
        
        if not parts:
            return None, None
        
        parts = sorted(parts, key=lambda x: x.get("release_date", ""))
        
        collection_name = data.get("name")
        print(f"   📚 Collection: {collection_name} ({len(parts)} filmes)")
        
        converted = []
        for i, movie in enumerate(parts, 1):
            year = movie.get("release_date", "")[:4]
            print(f"      {i}. {movie['title']} ({year})")
            
            converted.append({
                "id": movie["id"],
                "type": "movie",
                "title": movie["title"],
                "original_title": movie.get("original_title", ""),
                "release_date": movie.get("release_date", ""),
                "overview": movie.get("overview", ""),
                "year": year,
                "popularity": movie.get("popularity", 0),
                "title_similarity": 1.0,
                "collection_name": collection_name
            })
        
        return converted, collection_name
        
    except Exception as e:
        return None, None

def search_multi(title, year=None, get_all=False):
    """Busca multi"""
    try:
        url = f"{TMDB_BASE_URL}/search/multi"
        params = {
            "api_key": TMDB_API_KEY,
            "query": title,
            "language": "en-US"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("results"):
            return None
        
        results = [r for r in data["results"] if r.get("media_type") in ["movie", "tv"]]
        
        if not results:
            return None
        
        results = [r for r in results if r.get("popularity", 0) >= MIN_POPULARITY]
        
        if not results:
            return None
        
        for r in results:
            result_title = r.get("title") if r["media_type"] == "movie" else r.get("name", "")
            original_title = r.get("original_title") if r["media_type"] == "movie" else r.get("original_name", "")
            
            sim1 = title_similarity(title, result_title)
            sim2 = title_similarity(title, original_title)
            r["title_similarity"] = max(sim1, sim2)
        
        if not get_all:
            results = [r for r in results if r.get("title_similarity", 0) >= MIN_TITLE_SIMILARITY]
            
            if not results:
                return None
        
        if year:
            year_filtered = []
            for r in results:
                if r["media_type"] == "movie":
                    r_year = r.get("release_date", "")[:4]
                else:
                    r_year = r.get("first_air_date", "")[:4]
                
                if r_year == year:
                    year_filtered.append(r)
            
            if year_filtered:
                results = year_filtered
            else:
                return None
        
        results = sorted(results, key=lambda x: x.get("popularity", 0), reverse=True)
        
        print(f"   🔍 Encontrados {len(results)} resultado(s):")
        for i, r in enumerate(results[:10], 1):
            media_type = r["media_type"]
            result_title = r.get("title") if media_type == "movie" else r.get("name", "")
            year_field = "release_date" if media_type == "movie" else "first_air_date"
            result_year = r.get(year_field, "")[:4]
            icon = "🎬" if media_type == "movie" else "📺"
            
            print(f"      {i}. {icon} {result_title} ({result_year})")
        
        if not get_all:
            results = [results[0]]
        
        converted_results = []
        for result in results:
            media_type = result["media_type"]
            
            if media_type == "movie":
                release_year = result.get("release_date", "")[:4]
                
                converted_results.append({
                    "id": result["id"],
                    "type": "movie",
                    "title": result["title"],
                    "original_title": result.get("original_title", ""),
                    "release_date": result.get("release_date", ""),
                    "overview": result.get("overview", ""),
                    "year": release_year,
                    "popularity": result.get("popularity", 0),
                    "title_similarity": result.get("title_similarity", 0)
                })
            
            else:
                first_air_year = result.get("first_air_date", "")[:4]
                
                converted_results.append({
                    "id": result["id"],
                    "type": "tv",
                    "title": result["name"],
                    "original_title": result.get("original_name", ""),
                    "release_date": result.get("first_air_date", ""),
                    "overview": result.get("overview", ""),
                    "year": first_air_year,
                    "popularity": result.get("popularity", 0),
                    "title_similarity": result.get("title_similarity", 0)
                })
        
        return converted_results if get_all else converted_results[0]
        
    except Exception as e:
        return None

def get_tv_seasons(tv_id):
    """Lista temporadas"""
    try:
        url = f"{TMDB_BASE_URL}/tv/{tv_id}"
        params = {"api_key": TMDB_API_KEY, "language": "en-US"}
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        seasons = data.get("seasons", [])
        seasons = [s for s in seasons if s.get("season_number", 0) > 0]
        
        return [s["season_number"] for s in seasons]
    except Exception as e:
        return []

def get_season_images(tv_id, season_number):
    """Imagens de temporada"""
    try:
        url = f"{TMDB_BASE_URL}/tv/{tv_id}/season/{season_number}/images"
        params = {"api_key": TMDB_API_KEY}
        
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()
        
        all_posters = data.get("posters", [])
        posters = [p for p in all_posters if p.get("iso_639_1") is not None]
        
        return posters
    except Exception as e:
        return []

def get_images(content_id, content_type, season=None):
    """Obtém imagens"""
    try:
        if content_type == "tv" and season is not None:
            posters = get_season_images(content_id, season)
            backdrops = []
        else:
            url = f"{TMDB_BASE_URL}/{content_type}/{content_id}/images"
            params = {"api_key": TMDB_API_KEY}
            
            response = requests.get(url, params=params, timeout=20)
            response.raise_for_status()
            data = response.json()
            
            all_posters = data.get("posters", [])
            all_backdrops = data.get("backdrops", [])
            
            posters = [p for p in all_posters if p.get("iso_639_1") is not None]
            backdrops = [b for b in all_backdrops if b.get("iso_639_1") is not None]
        
        print(f"      📸 {len(posters)} posters", end="")
        if backdrops:
            print(f" | 🖼️  {len(backdrops)} backdrops")
        else:
            print()
        
        return posters, backdrops
    except Exception as e:
        return [], []

def generate_urls(file_path, sizes_dict):
    """Gera URLs"""
    urls = {}
    for device, size in sizes_dict.items():
        urls[device] = f"{TMDB_IMAGE_BASE}{size}{file_path}"
    return urls

def get_content_dir(content, season=None, collection_name=None):
    """Gera caminho da pasta com organização"""
    safe_title = "".join(c for c in content["title"] if c.isalnum() or c in (' ', '-', '_')).strip()
    year = content["year"]
    content_type = content["type"]
    
    # Se é filme de collection
    if collection_name and content_type == "movie":
        safe_collection = "".join(c for c in collection_name if c.isalnum() or c in (' ', '-', '_')).strip()
        base_dir = os.path.join(OUTPUT_DIR, safe_collection)
        
        if year:
            content_dir = os.path.join(base_dir, f"{safe_title} ({year})")
        else:
            content_dir = os.path.join(base_dir, safe_title)
    
    # Se é série
    elif content_type == "tv":
        series_dir = os.path.join(OUTPUT_DIR, f"[SERIE] {safe_title}")
        
        if season:
            content_dir = os.path.join(series_dir, f"Season {season}")
        else:
            content_dir = series_dir
    
    # Filme individual (sem collection)
    else:
        if year:
            content_dir = os.path.join(OUTPUT_DIR, f"{safe_title} ({year})")
        else:
            content_dir = os.path.join(OUTPUT_DIR, safe_title)
    
    return content_dir

def check_if_exists(content, season=None, collection_name=None):
    """Verifica existência"""
    content_dir = get_content_dir(content, season, collection_name)
    json_path = os.path.join(content_dir, "images.json")
    
    return os.path.exists(json_path), content_dir

def process_season(content, season_num):
    """Processa temporada"""
    print(f"      📺 Season {season_num}...")
    
    exists, content_dir = check_if_exists(content, season_num)
    
    if exists:
        print(f"         ⏭️  Já existe!")
        return "skipped"
    
    posters, backdrops = get_images(content["id"], "tv", season_num)
    
    if not posters:
        print(f"         ⚠️  Sem imagens")
        return None
    
    content_data = {
        "id": content["id"],
        "type": "tv",
        "season": season_num,
        "title": content["title"],
        "original_title": content["original_title"],
        "release_date": content["release_date"],
        "overview": content["overview"],
        "popularity": content.get("popularity", 0),
        "posters": [],
        "backdrops": []
    }
    
    for poster in posters:
        urls = generate_urls(poster["file_path"], POSTER_SIZES)
        content_data["posters"].append({
            "file_path": poster["file_path"],
            "language": poster.get("iso_639_1"),
            "vote_average": poster.get("vote_average", 0),
            "width": poster.get("width", 0),
            "height": poster.get("height", 0),
            "urls": urls
        })
    
    for backdrop in backdrops:
        urls = generate_urls(backdrop["file_path"], BACKDROP_SIZES)
        content_data["backdrops"].append({
            "file_path": backdrop["file_path"],
            "language": backdrop.get("iso_639_1"),
            "vote_average": backdrop.get("vote_average", 0),
            "width": backdrop.get("width", 0),
            "height": backdrop.get("height", 0),
            "urls": urls
        })
    
    os.makedirs(content_dir, exist_ok=True)
    json_path = os.path.join(content_dir, "images.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(content_data, f, indent=2, ensure_ascii=False)
    
    print(f"         💾 {content_dir}")
    return content_data

def process_item(item_info):
    """Processa item"""
    title = item_info["title"]
    year = item_info["year"]
    season = item_info["season"]
    
    print(f"🔍 {title}", end="")
    if year:
        print(f" ({year})")
    elif season == "all":
        print(" - TODAS TEMPORADAS")
    elif season:
        print(f" - S{season:02d}")
    else:
        print(" - TODAS AS VERSÕES")
    
    contents = None
    collection_name = None
    
    if year is None and season is None:
        print(f"   🔍 Procurando collection...")
        collection_id, coll_name = search_collection(title)
        
        if collection_id:
            print(f"   ✅ Collection: {coll_name}")
            contents, collection_name = get_collection_movies(collection_id)
    
    if not contents:
        get_all = (year is None and season is None)
        contents = search_multi(title, year, get_all=get_all)
    
    if not contents:
        return None
    
    if not isinstance(contents, list):
        contents = [contents]
    
    all_results = []
    
    for content in contents:
        type_icon = "🎬" if content["type"] == "movie" else "📺"
        print(f"\n   {type_icon} {content['title']} ({content['year']})")
        
        # Pegar collection_name do content se existir
        coll = content.get("collection_name", collection_name)
        
        if content["type"] == "movie" and season is not None:
            print(f"      ⚠️  É filme, ignorando temporada")
            season_to_use = None
        else:
            season_to_use = season
        
        if content["type"] == "tv" and season_to_use is not None:
            if season_to_use == "all":
                seasons = get_tv_seasons(content["id"])
                print(f"      📺 {len(seasons)} temporadas")
                
                for s in seasons:
                    result = process_season(content, s)
                    if result and result != "skipped":
                        all_results.append(result)
                
                continue
            else:
                result = process_season(content, season_to_use)
                if result and result != "skipped":
                    all_results.append(result)
                continue
        
        exists, content_dir = check_if_exists(content, None, coll)
        
        if exists:
            print(f"      ⏭️  Já existe!")
            continue
        
        posters, backdrops = get_images(content["id"], content["type"])
        
        if not posters and not backdrops:
            print(f"      ⚠️  Sem imagens")
            continue
        
        content_data = {
            "id": content["id"],
            "type": content["type"],
            "title": content["title"],
            "original_title": content["original_title"],
            "release_date": content["release_date"],
            "overview": content["overview"],
            "popularity": content.get("popularity", 0),
            "collection_name": coll,
            "posters": [],
            "backdrops": []
        }
        
        for poster in posters:
            urls = generate_urls(poster["file_path"], POSTER_SIZES)
            content_data["posters"].append({
                "file_path": poster["file_path"],
                "language": poster.get("iso_639_1"),
                "vote_average": poster.get("vote_average", 0),
                "width": poster.get("width", 0),
                "height": poster.get("height", 0),
                "urls": urls
            })
        
        for backdrop in backdrops:
            urls = generate_urls(backdrop["file_path"], BACKDROP_SIZES)
            content_data["backdrops"].append({
                "file_path": backdrop["file_path"],
                "language": backdrop.get("iso_639_1"),
                "vote_average": backdrop.get("vote_average", 0),
                "width": backdrop.get("width", 0),
                "height": backdrop.get("height", 0),
                "urls": urls
            })
        
        os.makedirs(content_dir, exist_ok=True)
        json_path = os.path.join(content_dir, "images.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(content_data, f, indent=2, ensure_ascii=False)
        
        print(f"      💾 {content_dir}")
        all_results.append(content_data)
    
    return all_results if all_results else None

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    items = read_movies_from_sheet()
    
    if not items:
        print("\n❌ Nenhum item!")
        return
    
    print(f"{'=' * 60}")
    print(f"Processando {len(items)} itens...")
    print(f"{'=' * 60}\n")
    
    all_content_data = []
    skipped = []
    
    for i, item_info in enumerate(items, 1):
        print(f"[{i}/{len(items)}] {item_info['original']}")
        print("-" * 60)
        
        try:
            result = process_item(item_info)
            
            if isinstance(result, list):
                all_content_data.extend(result)
            elif result:
                all_content_data.append(result)
            else:
                skipped.append(item_info["original"])
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            skipped.append(item_info["original"])
            import traceback
            traceback.print_exc()
        
        print()
    
    consolidated_path = os.path.join(OUTPUT_DIR, "all_content.json")
    with open(consolidated_path, 'w', encoding='utf-8') as f:
        json.dump(all_content_data, f, indent=2, ensure_ascii=False)
    
    print(f"{'=' * 60}")
    print(f"✅ CONCLUÍDO!")
    print(f"{'=' * 60}")
    print(f"📊 Total processados: {len(all_content_data)}")
    print(f"⚠️  Pulados: {len(skipped)}")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompido")
    except Exception as e:
        print(f"\n\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
