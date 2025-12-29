#!/usr/bin/env python3
"""
기사 통계 생성 스크립트
- 날짜별, 카테고리별 기사 수 통계
- 2025년 12월 데이터 기준
"""
import boto3
from collections import defaultdict
from datetime import datetime, timedelta
import csv
import sys

# DynamoDB 설정
TABLE_NAME = "seodaily-eng-articles-dev"
REGION = "us-east-1"

# 카테고리 목록 (이미지 순서대로)
CATEGORIES = [
    "IT_과학",
    "경제",
    "국제",
    "문화",
    "사회",
    "스포츠",
    "정치",
    "지역",
    "기타"
]

def get_all_articles():
    """DynamoDB에서 모든 기사 가져오기"""
    dynamodb = boto3.resource('dynamodb', region_name=REGION)
    table = dynamodb.Table(TABLE_NAME)

    articles = []
    last_evaluated_key = None

    print("DynamoDB에서 기사 데이터 가져오는 중...")

    while True:
        if last_evaluated_key:
            response = table.scan(
                ProjectionExpression="news_id, published_at, category",
                ExclusiveStartKey=last_evaluated_key
            )
        else:
            response = table.scan(
                ProjectionExpression="news_id, published_at, category"
            )

        articles.extend(response.get('Items', []))
        last_evaluated_key = response.get('LastEvaluatedKey')

        if not last_evaluated_key:
            break

        print(f"  {len(articles)}개 로드됨...")

    print(f"총 {len(articles)}개 기사 로드 완료")
    return articles


def extract_date_from_news_id(news_id: str) -> str:
    """news_id에서 날짜 추출 (YYYYMMDD 형식)"""
    # news_id 형식: 02100311.20251223092834001
    # 날짜는 뒤에 있는 8자리 (20251223)
    try:
        if '.' in news_id:
            date_part = news_id.split('.')[1][:8]
        else:
            date_part = news_id[:8]
        return date_part
    except:
        return None


def extract_date_from_published_at(published_at: str) -> str:
    """published_at에서 날짜 추출"""
    try:
        if published_at:
            # ISO 형식: 2025-12-23T09:28:34+09:00 또는 2025-12-23
            date_str = published_at[:10]  # YYYY-MM-DD
            return date_str.replace('-', '')  # YYYYMMDD
    except:
        pass
    return None


def normalize_category(category: str) -> str:
    """카테고리 정규화"""
    if not category:
        return "기타"

    # 영어 -> 한글 매핑
    category_map = {
        'finance': '경제',
        'economy': '경제',
        'technology': 'IT_과학',
        'it': 'IT_과학',
        'science': 'IT_과학',
        'politics': '정치',
        'society': '사회',
        'culture': '문화',
        'sports': '스포츠',
        'international': '국제',
        'world': '국제',
        'region': '지역',
        'local': '지역',
    }

    cat_lower = category.lower().strip()

    # 영어 카테고리 변환
    if cat_lower in category_map:
        return category_map[cat_lower]

    # 한글 카테고리는 그대로
    if category in CATEGORIES:
        return category

    # 부분 매칭
    for eng, kor in category_map.items():
        if eng in cat_lower:
            return kor

    return "기타"


def generate_statistics(articles, year=2025, month=12):
    """날짜별, 카테고리별 통계 생성"""
    # 통계 딕셔너리: {날짜: {카테고리: 개수}}
    stats = defaultdict(lambda: defaultdict(int))

    for article in articles:
        # 날짜 추출 (published_at 우선, 없으면 news_id에서)
        date_str = extract_date_from_published_at(article.get('published_at'))
        if not date_str:
            date_str = extract_date_from_news_id(article.get('news_id', ''))

        if not date_str:
            continue

        # 해당 월 데이터만 필터링
        try:
            article_year = int(date_str[:4])
            article_month = int(date_str[4:6])
            article_day = int(date_str[6:8])

            if article_year != year or article_month != month:
                continue

            date_key = f"{year}.{month}.{article_day}"
        except:
            continue

        # 카테고리 정규화
        category = normalize_category(article.get('category', ''))

        stats[date_key][category] += 1

    return stats


def is_weekend(year, month, day):
    """주말 여부 확인 (토요일=5, 일요일=6)"""
    try:
        date = datetime(year, month, day)
        return date.weekday() >= 5
    except:
        return False


def print_statistics(stats, year=2025, month=12):
    """통계 출력 (테이블 형식)"""

    # 헤더 출력
    header = ["날짜"] + CATEGORIES + ["합계"]
    print("\n" + "=" * 120)
    print(f"{year}년 {month}월 기사 통계")
    print("=" * 120)
    print("\t".join(header))
    print("-" * 120)

    # 주차별 합계
    weekly_totals = defaultdict(lambda: defaultdict(int))
    monthly_totals = defaultdict(int)

    # 해당 월의 일수 계산
    if month == 12:
        last_day = 31
    elif month in [4, 6, 9, 11]:
        last_day = 30
    elif month == 2:
        last_day = 29 if year % 4 == 0 else 28
    else:
        last_day = 31

    # 날짜별 출력
    for day in range(1, last_day + 1):
        date_key = f"{year}.{month}.{day}"

        if date_key not in stats:
            continue

        row_total = 0
        row = [date_key]

        for cat in CATEGORIES:
            count = stats[date_key].get(cat, 0)
            row.append(str(count) if count > 0 else "")
            row_total += count
            monthly_totals[cat] += count

        row.append(str(row_total))

        # 주차 계산 (1일부터 7일: 1주차, 8일~14일: 2주차, ...)
        week_num = (day - 1) // 7 + 1
        for cat in CATEGORIES:
            weekly_totals[week_num][cat] += stats[date_key].get(cat, 0)
        weekly_totals[week_num]['합계'] += row_total

        # 주말 표시 (빨간색 - 터미널에서)
        weekend = is_weekend(year, month, day)
        if weekend:
            print(f"\033[91m{chr(9).join(row)}\033[0m")  # 빨간색
        else:
            print("\t".join(row))

    # 구분선
    print("-" * 120)

    # 주차별 합계 출력
    for week_num in sorted(weekly_totals.keys()):
        row = [f"{week_num}주차"]
        week_total = 0
        for cat in CATEGORIES:
            count = weekly_totals[week_num].get(cat, 0)
            row.append(str(count) if count > 0 else "")
            week_total += count
        row.append(str(week_total))
        print("\t".join(row))

    # 전체 합계
    print("-" * 120)
    total_row = ["전체합계"]
    grand_total = 0
    for cat in CATEGORIES:
        total_row.append(str(monthly_totals[cat]))
        grand_total += monthly_totals[cat]
    total_row.append(str(grand_total))
    print("\t".join(total_row))

    print("=" * 120)

    return monthly_totals, grand_total


def export_to_csv(stats, year=2025, month=12, filename=None):
    """CSV 파일로 내보내기"""
    if filename is None:
        filename = f"article_statistics_{year}_{month:02d}.csv"

    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)

        # 헤더
        writer.writerow(["날짜"] + CATEGORIES + ["합계"])

        # 해당 월의 일수
        if month == 12:
            last_day = 31
        elif month in [4, 6, 9, 11]:
            last_day = 30
        elif month == 2:
            last_day = 29 if year % 4 == 0 else 28
        else:
            last_day = 31

        # 주차별 합계
        weekly_totals = defaultdict(lambda: defaultdict(int))
        monthly_totals = defaultdict(int)

        # 날짜별 데이터
        for day in range(1, last_day + 1):
            date_key = f"{year}.{month}.{day}"

            if date_key not in stats:
                continue

            row = [date_key]
            row_total = 0

            for cat in CATEGORIES:
                count = stats[date_key].get(cat, 0)
                row.append(count if count > 0 else "")
                row_total += count
                monthly_totals[cat] += count

            row.append(row_total)
            writer.writerow(row)

            # 주차 계산
            week_num = (day - 1) // 7 + 1
            for cat in CATEGORIES:
                weekly_totals[week_num][cat] += stats[date_key].get(cat, 0)
            weekly_totals[week_num]['합계'] += row_total

        # 빈 줄
        writer.writerow([])

        # 주차별 합계
        for week_num in sorted(weekly_totals.keys()):
            row = [f"{week_num}주차"]
            for cat in CATEGORIES:
                row.append(weekly_totals[week_num].get(cat, 0))
            row.append(weekly_totals[week_num]['합계'])
            writer.writerow(row)

        # 전체 합계
        writer.writerow([])
        total_row = ["전체합계"]
        grand_total = 0
        for cat in CATEGORIES:
            total_row.append(monthly_totals[cat])
            grand_total += monthly_totals[cat]
        total_row.append(grand_total)
        writer.writerow(total_row)

    print(f"\nCSV 파일 저장됨: {filename}")
    return filename


def main():
    # 연도/월 파라미터 (기본값: 2025년 12월)
    year = 2025
    month = 12

    if len(sys.argv) >= 3:
        year = int(sys.argv[1])
        month = int(sys.argv[2])

    print(f"\n{'='*60}")
    print(f"기사 통계 생성: {year}년 {month}월")
    print(f"{'='*60}")

    # 기사 데이터 가져오기
    articles = get_all_articles()

    # 통계 생성
    stats = generate_statistics(articles, year, month)

    # 터미널 출력
    monthly_totals, grand_total = print_statistics(stats, year, month)

    # CSV 내보내기
    csv_file = export_to_csv(stats, year, month)

    print(f"\n총 {grand_total}개 기사")


if __name__ == "__main__":
    main()
