#!/usr/bin/env python3
"""
DynamoDB 데이터 확인 스크립트
현재 저장된 기사들의 카테고리 분류 상태를 확인
"""

import boto3
from collections import Counter
import json
from datetime import datetime, timedelta

def check_dynamodb_categories():
    """DynamoDB에서 최근 기사들의 카테고리 분포 확인"""
    
    # DynamoDB 클라이언트 초기화
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('seodaily-eng-articles-dev')
    
    print("🔍 DynamoDB 카테고리 분석 시작...")
    print("=" * 60)
    
    # 최근 7일간의 데이터 확인
    seven_days_ago = datetime.now() - timedelta(days=7)
    seven_days_ago_str = seven_days_ago.strftime('%Y-%m-%d')
    
    try:
        # 전체 스캔 (최근 데이터만)
        response = table.scan(
            FilterExpression='published_at >= :date',
            ExpressionAttributeValues={
                ':date': seven_days_ago_str
            }
        )
        
        items = response['Items']
        
        # 페이지네이션 처리
        while 'LastEvaluatedKey' in response:
            response = table.scan(
                FilterExpression='published_at >= :date',
                ExpressionAttributeValues={
                    ':date': seven_days_ago_str
                },
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            items.extend(response['Items'])
        
        print(f"📊 최근 7일간 총 기사 수: {len(items)}")
        print()
        
        # 카테고리별 분포 확인
        categories = Counter()
        economic_articles = []
        
        for item in items:
            category = item.get('category', 'unknown')
            categories[category] += 1
            
            # 경제 관련 기사들 별도 수집
            if '경제' in str(category) or category in ['finance', 'markets', 'property', 'business']:
                economic_articles.append({
                    'news_id': item.get('news_id'),
                    'title_ko': item.get('title_ko', '')[:50] + '...',
                    'title_en': item.get('title_en', '')[:50] + '...',
                    'category': category,
                    'published_at': item.get('published_at')
                })
        
        # 전체 카테고리 분포
        print("📈 전체 카테고리 분포:")
        for category, count in categories.most_common():
            percentage = (count / len(items)) * 100
            print(f"  {category}: {count}개 ({percentage:.1f}%)")
        
        print()
        print("=" * 60)
        
        # 경제 카테고리 상세 분석
        print(f"💰 경제 관련 기사 상세 분석 (총 {len(economic_articles)}개):")
        print()
        
        if economic_articles:
            # 경제 기사들을 카테고리별로 그룹화
            economic_categories = Counter()
            for article in economic_articles:
                economic_categories[article['category']] += 1
            
            print("경제 카테고리별 분포:")
            for category, count in economic_categories.most_common():
                print(f"  {category}: {count}개")
            
            print()
            print("최근 경제 기사 샘플 (각 카테고리별 최대 3개):")
            
            # 카테고리별로 샘플 기사 표시
            shown_categories = set()
            for article in sorted(economic_articles, key=lambda x: x['published_at'], reverse=True):
                category = article['category']
                if category not in shown_categories or len([a for a in economic_articles if a['category'] == category and shown_categories]) < 3:
                    print(f"  [{category}] {article['title_ko']}")
                    print(f"    EN: {article['title_en']}")
                    print(f"    ID: {article['news_id']} | Date: {article['published_at']}")
                    print()
                    shown_categories.add(category)
        
        else:
            print("경제 관련 기사가 없습니다.")
        
        # 4개 경제 카테고리 확인
        print("=" * 60)
        print("🎯 4개 경제 카테고리 현황:")
        target_categories = ['markets', 'property', 'finance', 'business']
        
        for cat in target_categories:
            count = categories.get(cat, 0)
            print(f"  {cat}: {count}개")
            
            # 해당 카테고리의 최근 기사 1개 샘플
            sample = next((article for article in economic_articles if article['category'] == cat), None)
            if sample:
                print(f"    샘플: {sample['title_ko']}")
            else:
                print(f"    샘플: 없음")
        
        # 일반 '경제' 카테고리도 확인
        general_economy = categories.get('경제', 0)
        if general_economy > 0:
            print(f"  경제 (일반): {general_economy}개")
            sample = next((article for article in economic_articles if article['category'] == '경제'), None)
            if sample:
                print(f"    샘플: {sample['title_ko']}")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False
    
    return True

if __name__ == "__main__":
    check_dynamodb_categories()