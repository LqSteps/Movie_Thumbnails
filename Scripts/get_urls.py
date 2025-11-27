#!/usr/bin/env python3
"""
TMDB URL Generator - MODE: INFINITE POPULARITY (Images)
Recursos:
- Busca os Top Filmes e Séries Populares em lotes (infinito).
- Organiza em subpastas limpas.
- Gera URLs para todos os tamanhos de imagem.
- Pula automaticamente o que já foi baixado.
"""

import os
import requests
import json
import time
import re
import csv

# --- CONFIGURAÇÕES ---
TMDB_API_KEY = "20c117664b56c63145516208a9dd5f5f"
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/"
OUTPUT_DIR = "/GitHub/Repos/Movie_Thumbnails/Images"

# Configuração de Lotes
PAGES_PER_BATCH = 25  # 25 páginas = 500 itens por ciclo por tipo
MAX_TOTAL_PAGES = 500 # Limite da API (Rank 10.000)

# IDs para ignorar em TV (News, Reality, Talk)
IGNORED_GENRES = "10763,10764,10767"

POSTER_SIZES = {"mobile": "w342", "tablet": "w500", "desktop": "w780", "tv": "original"}
BACKDROP_SIZES = {"mobile": "w300", "tablet": "w780", "desktop": "w1280", "tv": "original"}

print("=" * 60)
print("🎬 TMDB URL Generator - INFINITE POPULARITY LOOP")
print("=" * 60)

# --- CACHE LOCAL ---

def get_existing_projects():
    """Mapeia pastas existentes para pular re-downloads"""
    if not os.path.exists(OUTPUT_DIR): return set()
    existing = set()
    print("📂 Atualizando índice local...")
    for root, dirs, files in os.walk(OUTPUT_DIR):
        for d in dirs:
            clean = re.sub(r'\[serie\]', '', d, flags=re.IGNORECASE)
            clean = re.sub(r'[^a-z0-9]', '', clean.lower())
            existing.add(clean)
            match = re.match(r'^(.*)(\d{4})$', clean)
            if match: existing.add(match.group(1))
    return existing

# --- API DISCOVERY ---

def fetch_batch(media_type, start_page, end_page):
    """Baixa lote de populares"""
    batch_results = []
    print(f"📡 Baixando {media_type.upper()}: Páginas {start_page} a {end_page}...")
    
    for page in range(start_page, end_page + 1):
        if page > MAX_TOTAL_PAGES: break
        try:
            url = f"{TMDB_BASE_URL}/discover/{media_type}"
            params = {
                "api_key": TMDB_API_KEY,
                "language": "en-US",
                "sort_by": "popularity.desc",
                "include_adult": "false",
                "include_video": "false",
                "page": page
            }
            if media_type == 'tv': params["without_genres"] = IGNORED_GENRES
            
            r = requests.get(url, params=params)
            if r.status_code == 200:
                res = r.json().get("results", [])
                for item in res:
                    item['media_type'] = media_type
                    batch_results.append(item)
            
            print(f"   📄 Lendo página {page}...", end="\r")
            time.sleep(0.05)
        except Exception as e:
            print(f"   ❌ Erro pg {page}: {e}")
            
    print(f"   ✅ {len(batch_results)} itens recuperados.")
    return batch_results

# --- PROCESSAMENTO ---

def generate_urls(file_path, sizes_dict):
    if not file_path: return {}
    return {k: f"{TMDB_IMAGE_BASE}{v}{file_path}" for k, v in sizes_dict.items()}

def get_content_dir(c, s=None):
    title = c.get("title", c.get("name", "Unknown"))
    safe = "".join(x for x in title if x.isalnum() or x in " -_").strip()
    date = c.get("release_date", c.get("first_air_date", ""))
    year = date[:4] if date and len(date) >= 4 else ""
    
    if c["media_type"] == "tv":
        base = os.path.join(OUTPUT_DIR, f"[SERIE] {safe}")
        return os.path.join(base, f"Season {s}") if s else base
    
    folder = f"{safe} ({year})" if year else safe
    return os.path.join(OUTPUT_DIR, folder)

def check_exists(path):
    return os.path.exists(os.path.join(path, "images.json"))

def save_json(path, data):
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, "images.json"), 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_images(cid, ctype, season=None):
    url = f"{TMDB_BASE_URL}/{ctype}/{cid}" + (f"/season/{season}/images" if season else "/images")
    try:
        r = requests.get(url, params={"api_key": TMDB_API_KEY})
        if r.status_code != 200: return [], []
        d = r.json()
        posters = [p for p in d.get("posters", []) if p.get("iso_639_1")]
        backdrops = [] if season else [b for b in d.get("backdrops", []) if b.get("iso_639_1")]
        return posters, backdrops
    except: return [], []

def get_tv_seasons(tid):
    try: return [s["season_number"] for s in requests.get(f"{TMDB_BASE_URL}/tv/{tid}", params={"api_key": TMDB_API_KEY}).json().get("seasons",[]) if s["season_number"] > 0]
    except: return []

def process_season(c, s):
    # print(f"      📺 Season {s}...") # Verbose off
    d = get_content_dir(c, s)
    if check_exists(d): return "skipped"
    
    posters, _ = get_images(c["id"], "tv", s)
    if not posters: return None
    
    data = {
        "id": c["id"], "type": "tv", "season": s, "title": c["name"],
        "posters": [{"path": p["file_path"], "lang": p["iso_639_1"], "urls": generate_urls(p["file_path"], POSTER_SIZES)} for p in posters]
    }
    save_json(d, data)
    return "processed"

def process_item(item, existing_cache):
    title = item.get("title", item.get("name"))
    date = item.get("release_date", item.get("first_air_date", ""))
    year = date[:4] if date and len(date)>=4 else ""
    
    clean_title = re.sub(r'[^a-z0-9]', '', title.lower())
    if f"{clean_title}{year}" in existing_cache or clean_title in existing_cache:
        return "skipped"

    print(f"⚡ Processando: {title} ({year}) [{item['media_type'].upper()}]")
    
    if item['media_type'] == 'tv':
        base_path = get_content_dir(item)
        if not os.path.exists(base_path): os.makedirs(base_path) # Cria pasta raiz se nao existir
        
        seasons = get_tv_seasons(item["id"])
        count = 0
        for s in seasons:
            if process_season(item, s) == "processed": count += 1
        if count > 0: print(f"      💾 Salvas {count} temporadas")
        
    else:
        d = get_content_dir(item)
        posters, backdrops = get_images(item["id"], "movie")
        
        if posters or backdrops:
            data = {
                "id": item["id"], "type": "movie", "title": title,
                "posters": [{"path": p["file_path"], "lang": p["iso_639_1"], "urls": generate_urls(p["file_path"], POSTER_SIZES)} for p in posters],
                "backdrops": [{"path": b["file_path"], "lang": b["iso_639_1"], "urls": generate_urls(b["file_path"], BACKDROP_SIZES)} for b in backdrops]
            }
            save_json(d, data)
            print(f"      💾 Imagens salvas")
            
    return "processed"

# --- MAIN LOOP ---

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    start_page = 1
    
    while start_page <= MAX_TOTAL_PAGES:
        end_page = min(start_page + PAGES_PER_BATCH - 1, MAX_TOTAL_PAGES)
        print(f"\n🔄 CICLO: Páginas {start_page}-{end_page}")
        print("-" * 60)
        
        existing = get_existing_projects()
        movies = fetch_batch('movie', start_page, end_page)
        tvs = fetch_batch('tv', start_page, end_page)
        
        all_items = movies + tvs
        all_items.sort(key=lambda x: x.get("popularity", 0), reverse=True)
        
        if not all_items: break
        
        print(f"🚀 Processando {len(all_items)} itens...")
        proc, skip = 0, 0
        
        for item in all_items:
            try:
                res = process_item(item, existing)
                if res == "processed": 
                    proc += 1
                    time.sleep(0.2)
                else: skip += 1
            except KeyboardInterrupt:
                print("\n🛑 Parando..."); return
            except Exception as e:
                print(f"❌ Erro: {e}")
        
        print("-" * 60)
        print(f"✅ CICLO FIM: Baixados {proc} | Pulados {skip}")
        print("-" * 60)
        
        start_page += PAGES_PER_BATCH
        if proc > 0: 
            print("⏳ Resfriando API...")
            time.sleep(5)

if __name__ == "__main__":
    main()
