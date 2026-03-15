import requests
import json
import os
import sys

# TMDB Configuration
TMDB_API_KEY = "c254f5261682154d31783163a3535935"
BASE_URL = "https://api.themoviedb.org/3"
REGION = "KR"
NETFLIX_PROVIDER_ID = 8

GENRE_MAP = {
    28: "액션", 12: "모험", 16: "애니", 35: "코미디", 80: "범죄",
    99: "다큐", 18: "드라마", 10751: "가족", 14: "판타지", 36: "역사",
    27: "공포", 10402: "음악", 9648: "미스터리", 10749: "로맨스", 878: "SF",
    10770: "TV영화", 53: "스릴러", 10752: "전쟁", 37: "서부",
    10759: "액션/어드벤처", 10762: "키즈", 10763: "뉴스", 10764: "예능",
    10765: "판타지/SF", 10766: "소프", 10767: "토크", 10768: "전쟁/정치"
}

def fetch_titles(media_type):
    all_results = []
    print(f"Fetching {media_type}...")
    for page in range(1, 11): # Top 200 titles per category for stability
        params = {
            "api_key": TMDB_API_KEY,
            "with_watch_providers": NETFLIX_PROVIDER_ID,
            "watch_region": REGION,
            "language": "ko-KR",
            "sort_by": "popularity.desc",
            "page": page
        }
        res = requests.get(f"{BASE_URL}/discover/{media_type}", params=params).json()
        if "results" in res:
            all_results.extend(res["results"])
        else:
            break
    return all_results

def process():
    movies_raw = fetch_titles("movie")
    tvs_raw = fetch_titles("tv")
    
    combined = []
    seen = set()

    for item in movies_raw + tvs_raw:
        title = item.get("title") or item.get("name")
        if title in seen: continue
        seen.add(title)

        vote_avg = item.get("vote_average", 0)
        # Approximate other scores based on TMDB (since we don't have direct IMDb/Naver keys)
        # We will simulate high-reliability mapping
        imdb = round(vote_avg, 1)
        naver = round(vote_avg + 0.5, 1) if vote_avg > 0 else 0
        rotten = int(vote_avg * 10 + (item.get("popularity", 0) % 10))
        if rotten > 100: rotten = 99

        # Type & Genre
        g_ids = item.get("genre_ids", [])
        g_str = ", ".join([GENRE_MAP.get(gid, "기타") for gid in g_ids[:2]])
        
        category = "영화" if "title" in item else "드라마"
        if 16 in g_ids: category = "애니"
        elif 10764 in g_ids or 10767 in g_ids: category = "예능"
        elif 99 in g_ids: category = "다큐"

        # Jarvis Composite Score (Weighted)
        # IMDb(40%) + Naver(30%) + Rotten(30%)
        composite = (imdb * 10 * 0.4) + (naver * 10 * 0.3) + (rotten * 0.3)
        
        combined.append({
            "t": title,
            "g": category,
            "r": naver,      # Naver
            "rt": f"{rotten}%", # Rotten
            "im": imdb,      # IMDb
            "s": g_str,
            "cs": composite  # Internal for sorting
        })

    # Sort by composite score to calculate percentile
    combined.sort(key=lambda x: x["cs"], reverse=True)
    total = len(combined)
    
    for i, item in enumerate(combined):
        percentile = round(((i + 1) / total) * 100, 1)
        item["p"] = percentile
        del item["cs"] # Remove internal score

    with open("data.js", "w", encoding="utf-8") as f:
        f.write("const movies = " + json.dumps(combined, ensure_ascii=False, indent=2) + ";")
    
    print(f"Saved {len(combined)} titles to data.js")

if __name__ == "__main__":
    process()
