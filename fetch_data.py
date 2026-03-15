import requests
import json
import time

TMDB_API_KEY = "c254f5261682154d31783163a3535935"
BASE_URL = "https://api.themoviedb.org/3"
NETFLIX_ID = 8
REGION = "KR"

def process():
    results = []
    seen = set()
    
    # 영화와 TV 시리즈 각각 수집 범위 확대
    for m_type in ["movie", "tv"]:
        print(f"Fetching {m_type} list...")
        for page in range(1, 21): 
            url = f"{BASE_URL}/discover/{m_type}?api_key={TMDB_API_KEY}&with_watch_providers={NETFLIX_ID}&watch_region={REGION}&sort_by=popularity.desc&page={page}&language=ko-KR"
            try:
                data = requests.get(url).json()
                items = data.get('results', [])
                for item in items:
                    title = item.get('title') or item.get('name')
                    if not title or title in seen: continue
                    seen.add(title)
                    
                    vote_avg = item.get('vote_average', 0)
                    
                    # 신뢰할 수 없는 데이터(네이버, 로튼)는 '-'로 처리하여 가공 방지
                    results.append({
                        "t": title,
                        "g": "영화" if m_type == "movie" else "드라마",
                        "im": round(vote_avg, 1) if vote_avg > 0 else "-", 
                        "r": "-", 
                        "rt": "-",
                        "s": "Netflix",
                        "p": 0,
                        "v": vote_avg # 정렬용
                    })
            except Exception as e:
                print(f"Error at page {page}: {e}")
            time.sleep(0.05)

    # 상위 % 계산 (실제 점수 기준 정렬)
    results.sort(key=lambda x: x['v'] if isinstance(x['v'], (int, float)) else 0, reverse=True)
    total = len(results)
    for i, item in enumerate(results):
        item['p'] = round(((i + 1) / total) * 100, 1)
        del item['v'] # 정렬용 임시 데이터 삭제

    with open("data.js", "w", encoding="utf-8") as f:
        f.write("const movies = " + json.dumps(results, ensure_ascii=False, indent=2) + ";")
    print(f"Total {len(results)} real titles updated.")

if __name__ == "__main__":
    process()
