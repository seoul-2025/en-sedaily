"""
Get recent articles with AI summary and their URLs
"""
import boto3
from config import Settings

settings = Settings()
dynamodb = boto3.resource('dynamodb', region_name=settings.aws_region)
table = dynamodb.Table(settings.dynamodb_table_articles)

# Get today's articles with AI summary
response = table.scan(
    FilterExpression='begins_with(published_at, :date) AND attribute_exists(ai_summary)',
    ExpressionAttributeValues={
        ':date': '2025-12-30'
    }
)

articles = response.get('Items', [])

while 'LastEvaluatedKey' in response:
    response = table.scan(
        FilterExpression='begins_with(published_at, :date) AND attribute_exists(ai_summary)',
        ExpressionAttributeValues={
            ':date': '2025-12-30'
        },
        ExclusiveStartKey=response['LastEvaluatedKey']
    )
    articles.extend(response.get('Items', []))

# Sort by published_at descending
articles.sort(key=lambda x: x.get('published_at', ''), reverse=True)

print(f"\n{'='*80}")
print(f"AI Summary가 추가된 기사들 (총 {len(articles)}개)")
print(f"{'='*80}\n")

for i, article in enumerate(articles[:10], 1):
    title = article.get('title_en', 'N/A')
    slug = article.get('slug', 'N/A')
    category = article.get('category', 'news')
    published_at = article.get('published_at', '')

    # Extract date parts from published_at
    if published_at:
        date_part = published_at[:10]  # 2025-12-30
        year, month, day = date_part.split('-')
        url = f"https://en.sedaily.com/{category}/{year}/{month}/{day}/{slug}"
    else:
        url = "N/A"

    print(f"{i}. {title[:70]}...")
    print(f"   URL: {url}")
    print(f"   Published: {published_at}")
    print()
