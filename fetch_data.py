#!/usr/bin/env python3
"""
NETFLIX SNIPER - DATA FETCHER
TMDB API로 한국 넷플릭스 전체 라이브러리를 수집하여 data.js 생성
--------------------------------------------------------------------
사용법:
  1. https://www.themoviedb.org 에서 무료 회원가입
  2. 프로필 > 설정 > API > API 키(v3) 발급 (즉시 발급됨)
  3. 아래 API_KEY 에 넣고 실행:
     python3 fetch_data.py YOUR_API_KEY_HERE
--------------------------------------------------------------------
"""

import urllib.request
import urllib.parse
import json
import sys
import time
import os

NETFLIX_PROVIDER_ID = 8   # TMDB 기준 Netflix = 8
REGION = "KR"             # 한국 넷플릭스
LANGUAGE = "ko-KR"
BASE_URL = "https://api.themoviedb.org/3"

# 장르 매핑 (TMDB 장르 ID → 한국어)
MOVIE_GENRES = {
    28:"액션", 12:"어드벤처", 16:"애니메이션", 35:"코미디", 80:"범죄",
    99:"다큐멘터리", 18:"드라마", 10751:"가족", 14:"판타지", 36:"역사",
    27:"공포", 10402:"음악", 9648:"미스터리", 10749:"로맨스", 878:"SF",
    10770:"TV 영화", 53:"스릴러", 10752:"전쟁", 37:"서부극"
}
TV_GENRES = {
    10759:"액션/어드벤처", 16:"애니메이션", 35:"코미디", 80:"범죄",
    99:"다큐멘터리", 18:"드라마", 10751:"가족", 10762:"키즈", 9648:"미스터리",
    10763:"뉴스", 10764:"리얼리티", 10765:"SF/판타지", 10766:"드라마",
    10767:"토크쇼", 10768:"전쟁/정치", 37:"서부극"
}

def fetch(api_key, path, params={}):
    params["api_key"] = api_key
    params["language"] = LANGUAGE
    url = f"{BASE_URL}{path}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"  [오류] {e}")
        return None

def get_all_pages(api_key, path, extra_params={}):
    results = []
    page = 1
    while True:
        params = {**extra_params, "page": page}
        data = fetch(api_key, path, params)
        if not data or "results" not in data:
            break
        results.extend(data["results"])
        total = data.get("total_pages", 1)
        print(f"  페이지 {page}/{min(total, 500)} ({len(results)}개 수집)", end="\r")
        if page >= total or page >= 500:  # TMDB 최대 500페이지
            break
        page += 1
        time.sleep(0.25)  # Rate limit 방지
    print()
    return results

def genres_to_str(genre_ids, genre_map):
    return "/".join([genre_map.get(gid, "") for gid in genre_ids[:2] if gid in genre_map]) or "기타"

def score_to_naver(vote):
    # TMDB 10점 기준 → 네이버 10점 환산 (약간 보정)
    return str(round(min(vote * 1.02, 10.0), 1)) if vote else "미평가"

def score_to_rt(vote, vote_count):
    # 투표 수 기반 RT 근사치
    if vote_count < 10: return "미평가"
    rt = int(min(vote * 10.5, 100))
    return f"{rt}%"

def main():
    if len(sys.argv) < 2:
        print("\n❌ API 키를 입력해주세요!")
        print("   사용법: python3 fetch_data.py YOUR_TMDB_API_KEY\n")
        print("   TMDB 무료 API 키 발급: https://www.themoviedb.org/settings/api\n")
        sys.exit(1)

    api_key = sys.argv[1].strip()
    print(f"\n🎬 NETFLIX SNIPER - DATA FETCHER")
    print(f"{'='*50}")
    print(f"🔑 API KEY: {api_key[:8]}...(확인중)")

    # API 키 테스트
    test = fetch(api_key, "/configuration")
    if not test:
        print("❌ API 키가 유효하지 않습니다. 다시 확인해주세요.")
        sys.exit(1)
    print(f"✅ API 키 인증 성공!\n")

    all_items = []

    # 1. 영화 수집
    print(f"📽️  [1/2] 넷플릭스 코리아 영화 수집 중...")
    movies_raw = get_all_pages(api_key, "/discover/movie", {
        "with_watch_providers": NETFLIX_PROVIDER_ID,
        "watch_region": REGION,
        "sort_by": "popularity.desc"
    })
    for m in movies_raw:
        if not m.get("title"): continue
        genre_ids = m.get("genre_ids", [])
        # 다큐멘터리(99) 별도 분류
        cat = "다큐" if 99 in genre_ids else "영화"
        all_items.append({
            "t": m["title"],
            "g": cat,
            "r": score_to_naver(m.get("vote_average", 0)),
            "rt": score_to_rt(m.get("vote_average", 0), m.get("vote_count", 0)),
            "s": genres_to_str(genre_ids, MOVIE_GENRES)
        })
    print(f"  ✅ 영화 {len(movies_raw)}개 수집 완료\n")

    # 2. TV/드라마 수집
    print(f"📺  [2/2] 넷플릭스 코리아 TV/드라마 수집 중...")
    tv_raw = get_all_pages(api_key, "/discover/tv", {
        "with_watch_providers": NETFLIX_PROVIDER_ID,
        "watch_region": REGION,
        "sort_by": "popularity.desc"
    })
    for t in tv_raw:
        if not t.get("name"): continue
        # 예능/애니/다큐 분류 추론
        genre_ids = t.get("genre_ids", [])
        if 16 in genre_ids:
            cat = "애니"
        elif 99 in genre_ids:
            cat = "다큐"
        elif 10764 in genre_ids or 10767 in genre_ids:
            cat = "예능"
        else:
            cat = "드라마"
        all_items.append({
            "t": t["name"],
            "g": cat,
            "r": score_to_naver(t.get("vote_average", 0)),
            "rt": score_to_rt(t.get("vote_average", 0), t.get("vote_count", 0)),
            "s": genres_to_str(genre_ids, TV_GENRES)
        })
    print(f"  ✅ TV/드라마 {len(tv_raw)}개 수집 완료\n")

    # 중복 제거 (제목 기준)
    seen = set()
    unique = []
    for item in all_items:
        if item["t"] not in seen:
            seen.add(item["t"])
            unique.append(item)

    print(f"{'='*50}")
    print(f"📊 최종 집계:")
    print(f"  영화:  {sum(1 for x in unique if x['g']=='영화')}개")
    print(f"  드라마: {sum(1 for x in unique if x['g']=='드라마')}개")
    print(f"  예능:  {sum(1 for x in unique if x['g']=='예능')}개")
    print(f"  애니:  {sum(1 for x in unique if x['g']=='애니')}개")
    print(f"  총합:  {len(unique)}개 (중복 제거 완료)\n")

    # data.js 저장
    output_path = os.path.join(os.path.dirname(__file__), "data.js")
    js_content = f"// NETFLIX SNIPER - AUTO GENERATED BY JARVIS\n// TMDB API 기준 넷플릭스 코리아 전체 라이브러리\n// 수집일: {time.strftime('%Y-%m-%d')}\n// 총 {len(unique)}개 타이틀\n\nconst movies = {json.dumps(unique, ensure_ascii=False, indent=2)};"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(js_content)

    print(f"✅ data.js 저장 완료! ({output_path})")
    print(f"🎯 이제 index.html을 열어서 저격하세요!\n")

if __name__ == "__main__":
    main()
