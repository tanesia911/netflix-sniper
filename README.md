# 🎯 NETFLIX SNIPER v5.0

> **"오늘 뭐 볼지 모르겠다면? 자비스한테 맡겨라."**  
> 한국 넷플릭스 전체 라이브러리 **8,422개** 중에서 오늘의 운명을 저격합니다.

![Y2K Win98 Style](https://img.shields.io/badge/UI-Y2K%20Win98-ff00ff?style=flat-square)
![Titles](https://img.shields.io/badge/Titles-8%2C422개-00ffff?style=flat-square)
![Source](https://img.shields.io/badge/Data-TMDB%20API-39ff14?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-Netflix%20KR-E50914?style=flat-square)

---

## ✨ 주요 기능

| 기능 | 설명 |
|---|---|
| 🎯 **랜덤 저격** | 버튼 하나로 오늘 볼 콘텐츠를 운명처럼 결정 |
| 🗂️ **6개 카테고리 필터** | 영화 / 드라마 / 다큐 / 애니 / 예능 / 전체 |
| 🚫 **중복 방지** | 최근 20개 히스토리 메모리 — 같은 것 절대 안 나옴 |
| ⭐ **이중 평점** | 네이버 평점 + 로튼 토마토 동시 표시 |
| 🎰 **룰렛 애니메이션** | 두근두근 무작위 슬롯머신 효과 |
| 🔊 **레트로 효과음** | Web Audio API 기반 8비트 비프음 |
| 📱 **모바일 최적화** | iPhone PWA 홈 화면 설치 지원 |
| 🗄️ **8,422개 실데이터** | TMDB API 기반 한국 넷플릭스 실제 라이브러리 |

---

## 📊 데이터 현황 (2026.03.15 기준)

```
🎬 영화    4,210개
📺 드라마   1,985개
🎥 다큐    1,147개
🎌 애니      614개
🎤 예능      466개
─────────────────
총합        8,422개  (중복 0%)
```

> 📡 데이터 출처: [TMDB API](https://www.themoviedb.org/documentation/api) — Netflix Korea (Provider ID: 8, Region: KR)

---

## 🚀 사용법

### 1. 바로 실행
```
index.html 파일을 브라우저에서 열기
```

### 2. 데이터 갱신 (넷플릭스 라이브러리 업데이트 시)
```bash
# TMDB 무료 API 키 발급: https://www.themoviedb.org/settings/api
python3 fetch_data.py YOUR_TMDB_API_KEY
```
약 7~10분 소요. 완료 시 `data.js` 자동 업데이트.

### 3. iPhone 홈 화면에 설치 (PWA)
```
Safari → 공유 버튼 → 홈 화면에 추가
```

---

## 📁 파일 구조

```
netflix-sniper/
├── index.html        # 메인 UI (Y2K Win98 스타일)
├── data.js           # 8,422개 타이틀 데이터베이스
├── fetch_data.py     # TMDB API 자동 수집 스크립트
└── README.md         # 이 파일
```

---

## 🛠️ 기술 스택

- **Frontend**: Vanilla HTML/CSS/JS (의존성 0)
- **UI Style**: Y2K Windows 98 + VT323 폰트
- **Data**: TMDB API v3 (Netflix KR Provider Filter)
- **Sound**: Web Audio API (8bit Square Wave)
- **데이터 수집**: Python 3 (표준 라이브러리만 사용)

---

## 🔄 데이터 갱신 주기 권장

| 빈도 | 이유 |
|---|---|
| 월 1회 | 넷플릭스 신규 콘텐츠 추가 반영 |
| 분기 1회 | 라이선스 만료된 작품 제거 |

---

## ⚠️ 주의사항

- 데이터는 TMDB 기준으로 실제 한국 넷플릭스 서비스 중인 콘텐츠입니다.
- 일부 콘텐츠는 라이선스 계약에 따라 실시간으로 추가/삭제될 수 있습니다.
- 정기적으로 `python3 fetch_data.py`를 실행하여 최신 상태를 유지하세요.

---

<p align="center">
  <b>(C) 2026 CEOK MULTIMEDIA SYSTEM</b><br>
  <i>Best viewed in Netscape 4.0 🦾</i>
</p>
