import requests
import os
from dotenv import load_dotenv
import time

# 1. API 키 로딩
load_dotenv()
API_KEY = os.getenv("BIGKINDS_KEY")
search_url = "https://tools.kinds.or.kr/search/news"

# 2. 설정
query = ""
from_date = "2025-12-01"
until_date = "2025-12-02"
fetch_count = 10000

# 3. 뉴스 검색 API 호출
search_payload = {
    "access_key": API_KEY,
    "argument": {
        "query": query,
        "published_at": {
            "from": from_date,
            "until": until_date
        },
        "provider": ["서울경제"],
        "category": [],
        "category_incident": [],
        "sort": { "date": "desc" },
        "return_from": 0,
        "return_size": fetch_count,
        "fields": ["title", "news_id", "published_at"]
    }
}

search_response = requests.post(search_url, json=search_payload)

# 4. 기사 리스트 추출
if search_response.status_code == 200 and search_response.json().get("result") == 0:
    search_result = search_response.json()
    search_docs = search_result["return_object"]["documents"]
    news_ids = [doc["news_id"] for doc in search_docs]
    print(f"총 {len(news_ids)}개의 뉴스 수집 완료!\n")
else:
    print("뉴스 검색 실패")
    print(search_response.text)
    exit()

# 5. 뉴스 조회 API 호출 (본문 확보)
view_payload = {
    "access_key": API_KEY,
    "argument": {
        "news_ids": news_ids,
        "fields": ["title", "content"]
    }
}

time.sleep(1)
view_response = requests.post(search_url, json=view_payload)

# 6. 결과 처리 및 출력
if view_response.status_code == 200 and view_response.json().get("result") == 0:
    view_docs = view_response.json()["return_object"]["documents"]
    
    for i, doc in enumerate(view_docs, 1):
        title = doc.get("title", "").strip()
        content = doc.get("content", "").strip()
        print(f"\n{i}.  제목: {title}")
        print(f"✍ 본문(앞부분): {content}…\n")
