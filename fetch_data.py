import requests
import json
import time
import os

# API Keys
TMDB_API_KEY = "c254f5261682154d31783163a3535935"
OMDB_API_KEY = "fe53f97e"

BASE_URL = "https://api.themoviedb.org/3"
OMDB_URL = "https://www.omdbapi.com/"

def get_netflix_titles(pages=30):
    all_titles = []
    
    # Genres to target specifically
    # 99: Documentary, 16: Animation, 10764: Reality, 10767: Talk
    target_genres = [None, 99, 16, 10764, 10767] 
    
    for media_type in ['movie', 'tv']:
        for genre in target_genres:
            genre_label = f"Genre:{genre}" if genre else "General"
            print(f"[*] Fetching {media_type} ({genre_label}) from TMDB...", flush=True)
            
            for page in range(1, pages + 1):
                url = f"{BASE_URL}/discover/{media_type}"
                params = {
                    "api_key": TMDB_API_KEY,
                    "with_networks": 213,
                    "with_watch_providers": 8,
                    "watch_region": "KR",
                    "language": "ko-KR",
                    "sort_by": "popularity.desc",
                    "page": page
                }
                if genre:
                    params["with_genres"] = genre
                
                try:
                    response = requests.get(url, params=params)
                    data = response.json()
                    
                    if 'results' in data:
                        for item in data['results']:
                            title = item.get('title') or item.get('name')
                            genre_ids = item.get('genre_ids', [])
                            category = "영화" if media_type == 'movie' else "드라마"
                            
                            # Detail genre string for UI
                            # Note: To get genre names, we'd need another call or a map. 
                            # For simplicity, we'll map the main ones.
                            genre_map = {
                                28: "액션", 12: "모험", 16: "애니", 35: "코미디", 80: "범죄", 
                                99: "다큐", 18: "드라마", 10751: "가족", 14: "판타지", 36: "역사", 
                                27: "공포", 10402: "음악", 9648: "미스터리", 10749: "로맨스", 
                                878: "SF", 10770: "TV영화", 53: "스릴러", 10752: "전쟁", 37: "서부",
                                10759: "액션/어드벤처", 10762: "키즈", 10763: "뉴스", 10764: "예능",
                                10765: "SF/판타지", 10766: "소프", 10767: "토크", 10768: "전쟁/정치"
                            }
                            main_genres = [genre_map.get(gid) for gid in genre_ids if genre_map.get(gid)]
                            genre_str = "/".join(main_genres[:3]) if main_genres else "기타"

                            if 99 in genre_ids: category = "다큐"
                            elif 16 in genre_ids: category = "애니"
                            elif 10764 in genre_ids or 10767 in genre_ids: category = "예능"
                            
                            all_titles.append({
                                "t": title,
                                "g": category,
                                "tmdb_id": item.get('id'),
                                "tmdb_vote": item.get('vote_average'),
                                "s": genre_str, # Use 's' field for genres now
                                "media_type": media_type
                            })
                    if page % 10 == 0:
                        print(f"    - Page {page} done.", flush=True)
                    time.sleep(0.05)
                except Exception as e:
                    print(f"[!] Error: {e}", flush=True)
                    
    return all_titles

def fetch_omdb_data(titles):
    print(f"[*] Fetching real IMDb/Rotten scores for {len(titles)} titles via OMDb...", flush=True)
    
    final_data = []
    count = 0
    session = requests.Session()
    
    for item in titles:
        count += 1
        title = item.get('t')
        category = item.get('g')
        media_type = item.get('media_type')
        genre_str = item.get('s')
        
        # Get IMDb ID from TMDB
        imdb_id = None
        try:
            ext_url = f"{BASE_URL}/{media_type}/{item['tmdb_id']}/external_ids"
            ext_res = session.get(ext_url, params={"api_key": TMDB_API_KEY}, timeout=5)
            imdb_id = ext_res.json().get('imdb_id')
        except:
            pass

        imdb_score = item['tmdb_vote']
        rotten_score = "-"
        
        if imdb_id:
            try:
                res = session.get(OMDB_URL, params={"apikey": OMDB_API_KEY, "i": imdb_id}, timeout=5)
                data = res.json()
                if data.get('Response') == 'True':
                    if data.get('imdbRating') and data['imdbRating'] != "N/A":
                        imdb_score = float(data['imdbRating'])
                    for r in data.get('Ratings', []):
                        if r['Source'] == 'Rotten Tomatoes':
                            rotten_score = int(r['Value'].replace('%', ''))
                            break
            except:
                pass
        
        final_data.append({
            "t": title,
            "g": category,
            "im": imdb_score,
            "rt": rotten_score,
            "s": genre_str,
            "p": 0
        })
        
        if count % 20 == 0:
            print(f"    - OMDb Progress: {count}/{len(titles)}", flush=True)
        if count >= 950: 
            print("[!] OMDb Limit reaching. Stopping.", flush=True)
            break
            
    return final_data

def calculate_percentiles(data):
    print("[*] Calculating honest percentiles based on IMDb scores...", flush=True)
    data.sort(key=lambda x: x['im'], reverse=True)
    total = len(data)
    for i, item in enumerate(data):
        percentile = round(((i + 1) / total) * 100, 1)
        item['p'] = percentile
    return data

if __name__ == "__main__":
    print("[*] Starting Netflix Data Extraction...", flush=True)
    raw_titles = get_netflix_titles(pages=30)
    
    # Deduplicate by title
    unique_titles = {}
    for r in raw_titles:
        if r['t'] not in unique_titles:
            unique_titles[r['t']] = r
            
    deduped = list(unique_titles.values())
    print(f"[*] Unique titles found: {len(deduped)}", flush=True)
    
    processed = fetch_omdb_data(deduped)
    final = calculate_percentiles(processed)
    
    output_path = os.path.expanduser("~/Desktop/netflix-sniper/data.js")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("const movies = ")
        json.dump(final, f, ensure_ascii=False, indent=2)
        f.write(";")
        
    print(f"[*] Success! {len(final)} titles saved to {output_path}", flush=True)
